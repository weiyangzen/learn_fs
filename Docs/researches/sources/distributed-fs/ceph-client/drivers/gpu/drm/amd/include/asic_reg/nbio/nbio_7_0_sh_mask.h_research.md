# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003068`: lines 1-2466, `Docs/researches/chunks/subset-b-003068_research.md`
- `subset-b-003069`: lines 2467-4969, `Docs/researches/chunks/subset-b-003069_research.md`
- `subset-b-003070`: lines 4970-7418, `Docs/researches/chunks/subset-b-003070_research.md`
- `subset-b-003071`: lines 7419-9885, `Docs/researches/chunks/subset-b-003071_research.md`
- `subset-b-003072`: lines 9886-12358, `Docs/researches/chunks/subset-b-003072_research.md`
- `subset-b-003073`: lines 12359-14814, `Docs/researches/chunks/subset-b-003073_research.md`
- `subset-b-003074`: lines 14815-17235, `Docs/researches/chunks/subset-b-003074_research.md`
- `subset-b-003075`: lines 17236-19637, `Docs/researches/chunks/subset-b-003075_research.md`
- `subset-b-003076`: lines 19638-22048, `Docs/researches/chunks/subset-b-003076_research.md`
- `subset-b-003077`: lines 22049-24433, `Docs/researches/chunks/subset-b-003077_research.md`
- `subset-b-003078`: lines 24434-26840, `Docs/researches/chunks/subset-b-003078_research.md`
- `subset-b-003079`: lines 26841-29278, `Docs/researches/chunks/subset-b-003079_research.md`
- `subset-b-003080`: lines 29279-31718, `Docs/researches/chunks/subset-b-003080_research.md`
- `subset-b-003081`: lines 31719-34187, `Docs/researches/chunks/subset-b-003081_research.md`
- `subset-b-003082`: lines 34188-36634, `Docs/researches/chunks/subset-b-003082_research.md`
- `subset-b-003083`: lines 36635-39058, `Docs/researches/chunks/subset-b-003083_research.md`
- `subset-b-003084`: lines 39059-41512, `Docs/researches/chunks/subset-b-003084_research.md`
- `subset-b-003085`: lines 41513-43979, `Docs/researches/chunks/subset-b-003085_research.md`
- `subset-b-003086`: lines 43980-46461, `Docs/researches/chunks/subset-b-003086_research.md`
- `subset-b-003087`: lines 46462-48915, `Docs/researches/chunks/subset-b-003087_research.md`
- `subset-b-003088`: lines 48916-51556, `Docs/researches/chunks/subset-b-003088_research.md`
- `subset-b-003089`: lines 51557-54232, `Docs/researches/chunks/subset-b-003089_research.md`
- `subset-b-003090`: lines 54233-56614, `Docs/researches/chunks/subset-b-003090_research.md`
- `subset-b-003091`: lines 56615-59014, `Docs/researches/chunks/subset-b-003091_research.md`
- `subset-b-003092`: lines 59015-61422, `Docs/researches/chunks/subset-b-003092_research.md`
- `subset-b-003093`: lines 61423-63822, `Docs/researches/chunks/subset-b-003093_research.md`
- `subset-b-003094`: lines 63823-66205, `Docs/researches/chunks/subset-b-003094_research.md`
- `subset-b-003095`: lines 66206-68539, `Docs/researches/chunks/subset-b-003095_research.md`
- `subset-b-003096`: lines 68540-70871, `Docs/researches/chunks/subset-b-003096_research.md`
- `subset-b-003097`: lines 70872-73204, `Docs/researches/chunks/subset-b-003097_research.md`
- `subset-b-003098`: lines 73205-75613, `Docs/researches/chunks/subset-b-003098_research.md`
- `subset-b-003099`: lines 75614-78264, `Docs/researches/chunks/subset-b-003099_research.md`
- `subset-b-003100`: lines 78265-80596, `Docs/researches/chunks/subset-b-003100_research.md`
- `subset-b-003101`: lines 80597-83011, `Docs/researches/chunks/subset-b-003101_research.md`
- `subset-b-003102`: lines 83012-85506, `Docs/researches/chunks/subset-b-003102_research.md`
- `subset-b-003103`: lines 85507-88072, `Docs/researches/chunks/subset-b-003103_research.md`
- `subset-b-003104`: lines 88073-90484, `Docs/researches/chunks/subset-b-003104_research.md`
- `subset-b-003105`: lines 90485-92893, `Docs/researches/chunks/subset-b-003105_research.md`
- `subset-b-003106`: lines 92894-95298, `Docs/researches/chunks/subset-b-003106_research.md`
- `subset-b-003107`: lines 95299-97677, `Docs/researches/chunks/subset-b-003107_research.md`
- `subset-b-003108`: lines 97678-100078, `Docs/researches/chunks/subset-b-003108_research.md`
- `subset-b-003109`: lines 100079-102486, `Docs/researches/chunks/subset-b-003109_research.md`
- `subset-b-003110`: lines 102487-104918, `Docs/researches/chunks/subset-b-003110_research.md`
- `subset-b-003111`: lines 104919-107381, `Docs/researches/chunks/subset-b-003111_research.md`
- `subset-b-003112`: lines 107382-109840, `Docs/researches/chunks/subset-b-003112_research.md`
- `subset-b-003113`: lines 109841-112318, `Docs/researches/chunks/subset-b-003113_research.md`
- `subset-b-003114`: lines 112319-114771, `Docs/researches/chunks/subset-b-003114_research.md`
- `subset-b-003115`: lines 114772-117356, `Docs/researches/chunks/subset-b-003115_research.md`
- `subset-b-003116`: lines 117357-118975, `Docs/researches/chunks/subset-b-003116_research.md`

## Chunk Research

### subset-b-003068: lines 1-2466

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 1-2466

## Purpose

This chunk is the opening section of AMDGPU's generated NBIO 7.0 shift/mask header. It defines bitfield offsets and masks for early NBIO/NBIF configuration spaces: northbridge configuration registers, the IOMMU L2 configuration capability block, root-complex PCIe configuration for BIF device 0, and the beginning of the matching BIF device 1 root-complex configuration block.

The header is hardware metadata, not executable logic. Its constants let AMDGPU register helpers encode field writes and decode register reads without hard-coding bit positions in driver C files. The companion NBIO 7.0 offset/default/SMN headers provide register addresses and reset/default values; this file supplies field geometry.

## Important APIs, Types, and Macros

There are no C functions, structs, typedefs, or enums in this chunk. The public interface is preprocessor constants named as:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset for a field inside a register.
- `<REGISTER>__<FIELD>_MASK`: field mask at its encoded position.

Lines 1-2466 contain 2,145 `#define` rows: the include guard plus 1,073 shift definitions and 1,071 complete mask definitions. The shift/mask imbalance is expected because the artificial chunk boundary stops after two shift definitions for `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP`; the remaining two shifts and all four masks for that register are on lines 2467-2472 in the next chunk.

Important register families in this range include:

- `NB_NBCFG0_*`: northbridge PCI configuration identity, command/status, revision/class, cache/latency/header, adapter ID, capability pointer, PCI control, SMN index/data windows, scratch registers, PCI arbitration, DRAM slot base/top-of-DRAM, index/data mutexes, and global NB performance counter control fields.
- `IOMMU_L2_0_IOMMU_*`: IOMMU L2 PCI identity and command/status fields, capability header/base/range/miscellaneous descriptors, MSI and MSI mapping capability fields, writable capability mirrors, MMIO/SMMU feature ID registers, DSFX/DSSX/DSCX dummy/control fields, DMA/host-response stall controls, and ARM SMMU-style ID registers.
- `BIF_CFG_DEV0_RC0_*`: a complete root-complex configuration namespace for NBIF device 0. It covers standard PCI bridge identity, command/status, BAR and bus range fields, bridge controls, power-management capability, PCIe capability, device/link/slot/root controls and statuses, MSI and SSID/MSI-map capability fields, vendor-specific and VC enhanced capabilities, device serial number, AER status/mask/severity/header-log/root-error fields, secondary PCIe capability, lane error status, lane 0-15 equalization controls, and ACS capability/control.
- `BIF_CFG_DEV1_RC0_*`: the beginning of the corresponding device 1 root-complex namespace. The chunk repeats the same PCI bridge, PM, PCIe, MSI, vendor-specific, and VC capability patterns through the first two shifts of `PCIE_VC0_RESOURCE_CAP`.

These constants are normally consumed by helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE`. The register address side comes from `nbio_7_0_offset.h` and `nbio_7_0_smn.h`.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. Including it gives the compiler symbols for mask-and-shift operations. Actual behavior is in AMDGPU NBIO, SOC15, PCIe, power-management, IOMMU, and error-handling code that reads or writes the registers.

The implied hardware flows are:

1. NB configuration fields expose device identity, command/status bits, SMN access windows, scratch registers, DRAM aperture metadata, index/data mutexes, and performance counter controls.
2. IOMMU L2 capability fields advertise and control translation unit capabilities, MSI delivery, SMMU MMIO exposure, feature IDs, stall behavior, DVM/DSFX support, and address-size/range metadata.
3. BIF device 0 root-complex fields describe bridge enumeration, memory and I/O forwarding windows, PME and link power controls, PCIe link speed/width negotiation, slot/hotplug controls, MSI routing, virtual channel allocation, PCIe advanced error reporting, lane equalization, and ACS policy.
4. BIF device 1 starts the same root-complex capability flow, but this chunk stops before its VC0 resource-capability definition is complete.

Because this is generated register metadata, control-flow risk is indirect: callers depend on these constants to preserve reserved bits, update only intended fields, and interpret hardware status correctly.

## State and Persistence

The header owns no runtime state, allocates no memory, performs no I/O, and persists nothing. The state represented here lives in NBIO 7.0 hardware registers.

State classes represented by the constants include:

- Enumerated PCI identity and capability metadata, such as vendor/device IDs, class/revision fields, capability pointers, PCIe capability versions, serial-number dwords, and feature capability bits.
- Writable configuration state, such as command enables, bridge windows, PME/MSI controls, link control, device control, VC arbitration controls, ACS controls, and IOMMU/SMMU enable or capability mirror fields.
- Hardware status/readback state, such as PCI status errors, link training/active status, slot status, root PME/error status, AER status/header logs, lane error status, and IOMMU/SMMU ID/status fields.
- Transient or side-effect-prone controls, including status clear fields, error masks/severity, link retrain/disable, function-level reset capability, IRQ/hotplug enables, VC table load controls, and index/data mutex unlock bits.

Reset values and retention across GPU reset, suspend/resume, PCI reset, or runtime power transitions are not defined here. Those semantics come from the NBIO hardware and companion default headers such as `nbio_7_0_default.h`.

## Dependencies and Integration Points

Primary companion generated headers are:

- `nbio_7_0_offset.h` for `cfg*` and `mm*` register offsets, including the registers named in this chunk.
- `nbio_7_0_default.h` for reset/default values.
- `nbio_7_0_smn.h` for SMN-addressed NBIO/PCIe registers outside ordinary config offsets.
- Adjacent chunks of `nbio_7_0_sh_mask.h`, especially the next chunk that completes `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP` and continues device 1 root-complex definitions.

In-tree include sites for this header include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, where NBIO 7.0 code combines offset, default, shift/mask, and SMN headers for doorbells, memory-controller access, register remapping, clock gating, and PCIe/NBIO register programming.
- `drivers/gpu/drm/amd/amdgpu/soc15.c`, where SOC15 common initialization includes NBIO 7.0 register metadata for Vega/Raven-era device setup.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`, which pulls NBIO 7.0 register metadata into SMU10/powerplay hardware-manager definitions.

Integration areas touched by these constants include PCI/PCIe enumeration, root-port bridge setup, NBIO index/SMN accesses, IOMMU discovery/configuration, MSI routing, link training and equalization, PCIe power management, hotplug/slot handling, AER/RAS reporting, ACS isolation, and NBIO clock/power-management paths.

## Risks

- Generated-header drift is the main risk. A wrong mask or shift silently makes `REG_SET_FIELD` or `REG_GET_FIELD` operate on the wrong hardware bits.
- The chunk boundary splits `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP`: only `PORT_ARB_CAP` and `REJECT_SNOOP_TRANS` shifts are inside this work item. Validators and merge logic must not treat the missing masks as source corruption.
- Many fields mirror PCI/PCIe architectural layouts. Small mistakes in bridge windows, link controls, AER masks, MSI addresses, VC mappings, or ACS controls can cause enumeration failures, interrupts routed incorrectly, hidden errors, peer-to-peer isolation gaps, or link instability.
- `BIF_CFG_DEV0_RC0_*` and `BIF_CFG_DEV1_RC0_*` are highly repetitive. Copy/paste or generator errors may only affect one root-complex instance and can be missed if tests exercise a single port.
- Several definitions include writable control bits adjacent to read-only status or reserved fields. Callers must use read-modify-write helpers carefully and preserve reserved bits.
- Error status, mask, and severity registers have very similar names. Confusing status fields with mask fields can leave PCIe errors uncleared, unreported, or misclassified.
- IOMMU and SMMU capability fields influence address translation, MSI delivery, and device range discovery. Bad masks here can break DMA isolation or produce misleading capability reporting.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware integration:

- Kernel build coverage with AMDGPU NBIO 7.0 users enabled catches missing, renamed, or syntactically invalid macros.
- Mechanical checks should verify that each complete register in lines 1-2466 has paired `__SHIFT` and `_MASK` definitions, while allowing the include guard and the known split at `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP`.
- Cross-header checks should compare register names in this chunk against `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, and `nbio_7_0_default.h` so addresses/defaults and bitfield metadata stay aligned.
- Symmetry checks should compare `BIF_CFG_DEV0_RC0_*` against the overlapping `BIF_CFG_DEV1_RC0_*` subset, ignoring only the device number and the artificial chunk ending.
- PCIe smoke tests on NBIO 7.0 ASICs should cover device enumeration, BAR and bridge-window programming, MSI delivery, link speed/width negotiation, link retrain/equalization, ASPM/power-management transitions, hotplug/slot status where applicable, ACS policy, and AER status/mask/reporting paths.
- IOMMU validation should exercise capability discovery, MSI mapping, MMIO/SMMU feature reporting, DMA translation/range setup, and error/status readback.
- Resume/reset tests should verify that driver reprogramming using these masks restores NBIO, BIF, IOMMU, PCIe link, interrupt, and error-reporting state after GPU reset or system suspend/resume.

## Chunk Boundary Notes

This chunk starts at the file header and includes complete address blocks for `nbio_iohub_nb_nbcfg_nb_cfgdec`, `nbio_iohub_iommu_l2_iommul2cfg`, and `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`. It then enters `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` and stops at line 2466 after the first two shifts for `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP`. The next chunk owns the remaining shifts and masks for that register plus the rest of the device 1 root-complex namespace.

### subset-b-003069: lines 2467-4969

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 2467-4969

## Scope

This chunk is a generated AMD NBIO 7.0 register shift/mask header segment. It contains C preprocessor constants only: `*_SHIFT` bit positions and `*_MASK` bit masks for PCIe/NBIO configuration-space fields. There are no C functions, structs, enums, variables, direct register reads or writes, allocation paths, locks, loops, or branches in this range.

The source path is under a local `ceph-client` source mirror, but this file is AMDGPU hardware metadata for the Linux DRM AMD driver. It is not Ceph filesystem logic.

The assigned range covers lines 2467-4969 of `nbio_7_0_sh_mask.h`. It starts in the middle of the `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP` field list, continues through the rest of the DEV1 root-complex PCIe extended-capability field masks, then covers two PCIe dummy configuration blocks, most of the DEV0 endpoint function 0 field masks including AER, ATS/PRI/PASID/SR-IOV and AMD GPUIOV vendor-specific fields, and ends inside the first DEV0 endpoint function 1 PCIe device capability block.

## Purpose

The purpose of this header segment is to publish symbolic bitfield definitions for NBIO 7.0 PCI/PCIe configuration registers. AMDGPU code pairs these macros with register offsets from `nbio_7_0_offset.h` when extracting fields from register values or composing values for read/modify/write operations.

Each logical register is represented by one or more `__<FIELD>__SHIFT` constants and matching `__<FIELD>_MASK` constants. The macros describe how a field is packed in the register, not whether that field is writable, read-only, sticky, write-one-to-clear, firmware-owned, PCI-core-owned, or safe for a driver-side update.

## Important Macro Families

The opening `BIF_CFG_DEV1_RC0_PCIE_*` portion finishes the DEV1 root-complex PCIe extended capability map. It covers virtual-channel resources for VC0 and VC1, serial-number extended capability dwords, AER capability fields, uncorrectable/correctable error status, masks and severity controls, header and TLP-prefix logs, root-error command/status/source ID fields, secondary PCIe link-control and lane-equalization fields for lanes 0 through 15, and ACS capability/control masks. These names are prefixed with `BIF_CFG_DEV1_RC0_`, distinguishing this root-complex view from the unprefixed DEV0 EPF0 endpoint view later in the chunk.

The `NB_PCIEDUMMY0_0_*` and `NB_PCIEDUMMY1_0_*` blocks provide compact dummy PCIe configuration images. Each has vendor/device identity fields, status/command bits, class-code/revision fields, and header-type fields. These are small decode surfaces compared with the full endpoint/root-complex blocks.

The `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` block uses mostly unprefixed names such as `COMMAND`, `STATUS`, `DEVICE_CAP`, `PCIE_UNCORR_ERR_STATUS`, and `PCIE_SRIOV_CONTROL`. It defines DEV0 endpoint function 0 PCI configuration-space field layout. The first part mirrors standard PCI header and capability fields: vendor/device ID, command/status, revision/class, BARs, ROM BAR, capability pointer, interrupt line/pin, vendor capability, power management capability/status, PCIe capability, device/link capability/control/status, Device/Link Capability 2, MSI, MSI-X table/PBA, vendor-specific capability, virtual-channel capability, serial number, AER, and BAR enhanced capability.

The EPF0 AER block is detailed. It includes uncorrectable error status/mask/severity fields for DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, AtomicOp egress blocked, and TLP prefix blocked conditions. Correctable error status/mask fields include receiver error, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, corrected internal error, and header-log overflow. AER capability/control fields include first-error pointer, ECRC generation/check capability and enable bits, multiple-header recording, TLP prefix log present, completion-timeout prefix/header log capability, and log overflow status.

The EPF0 PCIe feature-capability portion covers power budget, dynamic power allocation, secondary PCIe link-control/equalization, ACS, ATS, page request interface, PASID, TPH requester, multicast, LTR, ARI, and SR-IOV. These fields are important to DMA isolation, address translation, peer routing, virtualization, PCIe ordering, and platform power policy. For example, ATS control includes `STU` and `ATC_ENABLE`, PRI has enable/reset/status and outstanding request counters, PASID has enable and permission-mode bits, and SR-IOV has VF enable, migration, VF memory-space enable, ARI hierarchy, VF counts, VF BARs, supported/system page size, and migration-state array fields.

The AMD GPUIOV vendor-specific extended capability block starts at `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST_GPUIOV` and is one of the most hardware-specific parts of this slice. It includes VSEC list/header fields, `SRIOV_SHADOW` fields for VF enable and VF number, interrupt enable/status bits for GFX/UVD/VCE command-complete, self-recovered hang, FLR-needed hang, VM-busy transition events, plus HVVM mailbox transmit-ack and receive-valid interrupts. It also defines `RESET_CONTROL` for software PF FLR, `HVVM_MBOX_DW0` message/index fields, `HVVM_MBOX_DW1` per-VF `TRN_ACK` and `RCV_VALID` bits for VF0 through VF15, `HVVM_MBOX_DW2` PF ack/valid bits, GPUIOV context and frame-buffer accounting fields, per-VF frame-buffer base/size fields for VF0 through VF15, and scheduler dwords for UVD, VCE, and GFX.

The closing `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` block begins the DEV0 endpoint function 1 field map. In this chunk it covers standard PCI identity/header fields through `BIF_CFG_DEV0_EPF1_0_DEVICE_CAP`. The next chunk must cover the rest of EPF1 PCIe capabilities and extended capabilities.

## APIs, Types, And Functions

This chunk exports no typed API. Its public interface is the set of preprocessor macro names made visible by including `nbio_7_0_sh_mask.h`.

The practical API contract is the generated AMDGPU register-header convention:

- `nbio_7_0_offset.h` provides register offsets for the same logical register names.
- `nbio_7_0_sh_mask.h` provides field shifts and masks for those registers.
- `nbio_7_0_default.h` provides reset/default values for selected registers.
- Including code uses masks and shifts with register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and explicit bit operations around AMDGPU register accessors.

Because this is a generated mask header, consumers depend on exact spelling and namespace matching. The unprefixed EPF0 macros, the `BIF_CFG_DEV1_RC0_` root-complex macros, and the `BIF_CFG_DEV0_EPF1_0_` endpoint-function-1 macros are separate register namespaces even when they describe similar PCIe standard fields.

## Control Flow

There is no executable control flow in this header. Runtime control flow occurs in including code:

1. Driver code reads a PCIe/NBIO register through an AMDGPU access path or obtains a configuration value through a PCI/config-space path.
2. It applies one of these `*_MASK` values and shifts by the matching `*_SHIFT` to decode a field.
3. For writable fields, it composes a new value using the mask/shift pair, usually through AMDGPU helper macros, and writes it back through the relevant hardware access path.
4. Hardware, firmware, the Linux PCI core, the PF driver, or a virtualization manager observes or updates the underlying state depending on field ownership.

The chunk itself does not sequence device initialization, link training, SR-IOV enablement, mailbox handshakes, AER handling, or reset. It only defines the bit positions those paths must use when they touch NBIO 7.0 registers.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed state in PCI/PCIe configuration and vendor-specific extended capability registers.

The represented state includes PCI identity and class fields, command/status bits, BAR and ROM BAR address fields, power-management state, PCIe device/link/slot capabilities and controls, MSI/MSI-X configuration, VC arbitration state, AER status/mask/severity/log registers, secondary PCIe lane-equalization controls and lane error status, ACS routing controls, ATS/PRI/PASID address-translation controls, TPH requester policy, multicast controls, LTR capability values, ARI next-function and function-group controls, SR-IOV VF enumeration and VF BAR/page-size/migration state, and AMD GPUIOV PF/VF mailbox, interrupt, reset, context, frame-buffer, and scheduler state.

Ownership is mixed. Generic PCI header and capability fields overlap Linux PCI core ownership. AER fields may be hardware-updated and sometimes sticky. SR-IOV and GPUIOV fields are typically PF or virtualization-manager owned. ATS/PRI/PASID fields cross driver, IOMMU, and PCIe core policy. The mask header does not encode those ownership rules or side effects.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.0 register database staying synchronized. Register names in this file need to align with offset macros in `nbio_7_0_offset.h` and defaults in `nbio_7_0_default.h`. A mismatch can compile if all macros still exist, but the driver may manipulate the wrong bitfield.

The direct integration domain is AMDGPU NBIO and PCIe support. The constants are relevant anywhere NBIO 7.0 code decodes or programs PCIe configuration-space fields, link controls, AER handling, interrupt setup, SR-IOV virtualization, or GPU IOV mailbox state.

The Linux PCI core is an implicit integration point. Standard PCIe fields such as command/status, PM, MSI/MSI-X, AER, ACS, ATS, PASID, PRI, ARI, LTR, and SR-IOV have generic kernel policy and enumeration behavior. AMDGPU-specific code must avoid treating generic PCI-owned fields as private NBIO state unless the access is intentionally hardware-specific and coordinated.

IOMMU and virtualization paths are also key integration points. ATS, PRI, PASID, ACS, ARI, SR-IOV, VF BAR, migration, and GPUIOV fields affect DMA translation, peer routing, VF exposure, PF/VF isolation, mailbox delivery, reset handling, and frame-buffer partitioning.

Hardware diagnostics and reliability paths integrate through AER and lane-status fields. Uncorrectable/correctable error masks, severities, root-error reporting, header/TLP-prefix logs, link control 3, and per-lane equalization masks are the bit definitions consumers need when collecting error evidence or changing PCIe error policy.

## Risks And Edge Cases

- These are untyped preprocessor constants. A stale or incorrect mask/shift can compile cleanly and still corrupt PCIe configuration or decode status incorrectly.
- The namespace is repetitive and easy to confuse. `BIF_CFG_DEV1_RC0_PCIE_*`, unprefixed `PCIE_*`, and `BIF_CFG_DEV0_EPF1_0_PCIE_*` may describe analogous standard PCIe fields for different functions or hardware views.
- The chunk boundaries are artificial. The range begins after the first two `BIF_CFG_DEV1_RC0_PCIE_VC0_RESOURCE_CAP` field definitions and ends before the full EPF1 PCIe capability set, so whole-file conclusions require adjacent chunk reports.
- Standard PCIe fields have side effects and ownership rules not visible here. Status and AER bits can be sticky or write-one-to-clear; control fields can trigger link, reset, interrupt, or translation behavior.
- AER log and mask/severity fields are diagnostic-critical. Incorrect masks or field extraction can hide root causes, misclassify fatal/non-fatal errors, or clear evidence during read/modify/write sequences.
- ATS, PRI, PASID, ACS, ARI, SR-IOV, and multicast fields affect DMA routing and isolation. Wrong bit definitions or namespace mixups can break IOMMU translation, allow unintended peer traffic, expose VFs incorrectly, or destabilize passthrough/virtualization.
- GPUIOV mailbox and interrupt fields have dense per-engine and per-VF packing. An off-by-one VF bit, wrong ack/valid bit, or wrong interrupt mask can lose PF/VF messages, route events to the wrong VF, or wedge virtualization management.
- Per-VF frame-buffer allocation fields and total frame-buffer accounting are packed as base/limit or available/consumed fields. Bad masks can mis-partition VRAM or cause VF-visible memory ranges to overlap.
- Lane equalization fields are repeated for lanes 0 through 15. Copy or generation drift between lane numbers can make link-training diagnostics or overrides target the wrong physical lane.
- Several fields use full-width masks such as `0xFFFFFFFFL`, while others use narrow 8/16-bit masks in 32-bit registers. Consumers must preserve reserved bits when updating writable fields.

## Test Signals

Useful validation is mostly build-time, generated-header consistency, and hardware integration:

- Build AMDGPU configurations that include NBIO 7.0 support. Missing or renamed field macros should surface in code that includes `nbio_7_0_sh_mask.h`.
- Cross-check this mask range against `nbio_7_0_offset.h` for matching logical register names across DEV1 RC0, DEV0 EPF0, dummy PCIe blocks, and DEV0 EPF1.
- Run basic PCIe enumeration and device bring-up on NBIO 7.0 ASICs, watching command/status, BAR sizing, PM capability, PCIe capability, MSI/MSI-X, AER, and link-status paths.
- Exercise PCIe error reporting with platform AER diagnostics where available, confirming uncorrectable/correctable status, mask, severity, root-error status, source ID, header log, and TLP-prefix log fields decode as expected.
- Validate link training and recovery paths at supported link speeds and widths, including Link Control 3 and lane 0-15 equalization/status reporting.
- Run SR-IOV scenarios with PF/VF enumeration, VF enable/disable, VF memory-space enable, VF BAR exposure, VF page-size programming, VF migration-state fields, PF/VF reset, and MSI/MSI-X delivery.
- Exercise GPU IOV mailbox flows, checking HVVM mailbox `TRN_ACK`/`RCV_VALID` bits for VF0-VF15, PF ack/valid bits, GPUIOV interrupt enable/status fields, and GFX/UVD/VCE scheduler dword handling.
- Test IOMMU-backed features where platform support exists: ACS routing, ATS enablement, PRI page request handling, PASID enablement and permission bits, ARI next-function behavior, TPH requester configuration, and multicast/LTR policy.
- Use suspend/resume, runtime power management, GPU reset, FLR, and passthrough stress as integration tests because these paths combine PCIe status/control, AER, SR-IOV, ATS/PASID, and GPUIOV reset/mailbox state.

## Chunk Notes

- Lines 2467-2976 finish DEV1 RC0 PCIe VC, serial-number, AER, root-error, secondary PCIe, lane equalization, and ACS field masks.
- Lines 2977-3028 cover two small `NB_PCIEDUMMY*_0` PCIe dummy configuration blocks.
- Lines 3029-4432 cover DEV0 EPF0 standard PCI header fields, PM/PCIe/MSI/MSI-X, VC, serial number, AER, BAR enhanced, power budget, DPA, secondary PCIe, ACS, ATS, PRI, PASID, TPH, multicast, LTR, ARI, and SR-IOV fields.
- Lines 4433-4768 cover the AMD GPUIOV vendor-specific capability: VSEC header, SR-IOV shadow, GPUIOV interrupt enable/status, soft PF FLR, HVVM mailbox dwords, context, frame-buffer accounting, per-VF frame-buffer fields, and UVD/VCE/GFX scheduler dwords.
- Lines 4769-4969 begin DEV0 EPF1 standard PCI/PM/PCIe capability masks and stop inside `BIF_CFG_DEV0_EPF1_0_DEVICE_CAP`; the remainder of EPF1 is outside this work item.

### subset-b-003070: lines 4970-7418

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 4970-7418

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register shift/mask header. It contains preprocessor constants only: each hardware register field is represented by a `<REGISTER>__<FIELD>__SHIFT` macro and a matching `<REGISTER>__<FIELD>_MASK` macro for packing or extracting bitfields from PCI configuration-space and NBIO register values. There are no functions, structs, variables, includes, allocation paths, locks, direct register accesses, or executable branches in this range.

The selected lines start in the middle of endpoint/function `BIF_CFG_DEV0_EPF1_0` PCIe capability definitions, covering the tail of `DEVICE_CAP` masks and then the rest of EPF1's PCIe device/link, MSI/MSI-X, VSEC, virtual-channel, AER, BAR sizing, power-budgeting, DPA, secondary PCIe, per-lane equalization, ACS/ATS/PASID/TPH/MC/LTR/ARI/SR-IOV, and AMD GPU-IOV vendor-specific capability fields. The range then switches at line 6509 to address block `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` and defines the start of `BIF_CFG_DEV0_EPF2_0`, including conventional PCI config header fields, PM and PCIe capabilities, MSI/MSI-X, SATA capability fields, VSEC, AER, BAR sizing, power budgeting, DPA, ACS, and the beginning of ARI control.

Although the repository path is under a `ceph-client` source mirror, this source is AMDGPU DRM hardware metadata. It does not implement Ceph filesystem behavior, distributed filesystem state, networking, or storage persistence.

## Important APIs, Types, And Constants

There are no callable APIs or C types in this chunk. The exported interface is the generated macro namespace:

- `<REGISTER>__<FIELD>__SHIFT`: the field's low bit position.
- `<REGISTER>__<FIELD>_MASK`: the already-positioned field mask.

Major EPF1 register families in this chunk include:

- `BIF_CFG_DEV0_EPF1_0_DEVICE_*` and `LINK_*`: PCIe device capability/control/status and link capability/control/status fields, including payload size, read-request size, relaxed ordering, no-snoop, FLR initiation, completion timeout, LTR, OBFF, target link speed, link training, equalization, and de-emphasis/status bits.
- `BIF_CFG_DEV0_EPF1_0_MSI*` and `MSIX*`: MSI/MSI-X capability IDs, next pointers, enable and multiple-message controls, 32/64-bit message addresses/data, mask and pending bits, table size, function mask, table BIR/offset, and PBA BIR/offset.
- `BIF_CFG_DEV0_EPF1_0_PCIE_VENDOR_SPECIFIC*`, `PCIE_VC*`, and `PCIE_DEV_SERIAL_NUM*`: vendor-specific enhanced capability list/header fields, virtual-channel capability/control/status and VC0/VC1 resource maps, plus device serial number data words.
- `BIF_CFG_DEV0_EPF1_0_PCIE_ADV_ERR_*`: AER enhanced capability, uncorrectable error status/mask/severity, correctable error status/mask, advanced error capability/control, header logs, and TLP prefix logs. The uncorrectable sets include DLP, surprise down, poison, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC-blocked TLP, atomic egress block, and TLP prefix block fields.
- `BIF_CFG_DEV0_EPF1_0_PCIE_BAR*`: BAR enhanced capability plus BAR1 through BAR6 size-supported and control fields for BAR index, total count, and selected size.
- `BIF_CFG_DEV0_EPF1_0_PCIE_PWR_BUDGET*` and `PCIE_DPA*`: power budgeting data selection/data/capability fields and dynamic power allocation capability/status/control/substate power allocation fields.
- `BIF_CFG_DEV0_EPF1_0_PCIE_SECONDARY*` and `PCIE_LANE_*_EQUALIZATION_CNTL`: secondary PCIe capability/control fields and lane 0 through lane 15 equalization controls for downstream/upstream port transmit preset and preset hints.
- `BIF_CFG_DEV0_EPF1_0_PCIE_ACS*`, `ATS*`, `PAGE_REQ*`, `PASID*`, `TPH_REQR*`, `MC*`, `LTR*`, and `ARI*`: IOMMU/virtualization-related capabilities for ACS isolation, address translation service, page request, PASID width and enable, TPH requester controls, multicast address/receive/block maps, latency tolerance reporting, and alternative routing-ID interpretation.
- `BIF_CFG_DEV0_EPF1_0_PCIE_SRIOV*`: SR-IOV capability/control/status and VF enumeration/layout fields, including VF count, first VF offset, VF stride, VF device ID, supported/system page sizes, VF BARs, and migration state array offset.
- `BIF_CFG_DEV0_EPF1_0_PCIE_VENDOR_SPECIFIC_*_GPUIOV*`: AMD GPU-IOV VSEC fields for VSEC ID/revision/length, SR-IOV shadow VF enable/count, interrupt enable/status for GFX/UVD/VCE command complete, hang/self-recovery/FLR-needed, VM busy transition, and HVVM mailbox events, soft PF FLR, HVVM mailbox data and per-VF ack/valid bits, PF ack/valid bits, context and total framebuffer fields, per-VF framebuffer sizing for VF0 through VF15, and UVD/VCE/GFX scheduler dwords.

Major EPF2 register families in this chunk include:

- `BIF_CFG_DEV0_EPF2_0_VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class/header/BIST/BAR/adapter/ROM/capability-pointer/interrupt/min-grant/max-latency fields. These mirror the conventional PCI configuration header for endpoint function 2.
- `BIF_CFG_DEV0_EPF2_0_PMI*`, `SBRN`, `FLADJ`, and `DBESL_DBESLD`: power-management capability/status/control and USB/SATA-style timing/control metadata.
- `BIF_CFG_DEV0_EPF2_0_PCIE_CAP*`, `DEVICE_*`, and `LINK_*`: PCIe capability list, device and link capability/control/status, device/link capability 2 and control/status 2, and slot capability/control/status 2 fields.
- `BIF_CFG_DEV0_EPF2_0_MSI*`, `MSIX*`, and `SATA_*`: MSI/MSI-X programming fields plus SATA capability/index/data fields.
- `BIF_CFG_DEV0_EPF2_0_PCIE_VENDOR_SPECIFIC*`, `PCIE_ADV_ERR_*`, `PCIE_BAR*`, `PCIE_PWR_BUDGET*`, `PCIE_DPA*`, `PCIE_ACS*`, and `PCIE_ARI*`: the EPF2 subset of vendor-specific, AER, BAR sizing, power-budgeting, DPA, ACS, and ARI field layouts. The chunk ends after the ARI control shift macros; matching ARI control masks continue in the next chunk.

## Control Flow

This header has no runtime control flow. It is compile-time hardware metadata consumed by C code that performs register read/modify/write operations.

Typical consumer flow is:

1. Driver code includes `nbio_7_0_offset.h` and `nbio_7_0_sh_mask.h`, and sometimes `nbio_7_0_default.h` or `nbio_7_0_smn.h`.
2. A consumer reads a 16-bit or 32-bit PCIe/NBIO register through AMDGPU helpers, or prepares a value to write to a configuration-space register.
3. Field values are inserted with generated shifts and masks, usually indirectly through helpers such as `REG_SET_FIELD` or extracted through `REG_GET_FIELD`-style logic.
4. The programmed value is written back through SOC15, PCIe, or SMN/MMIO access helpers. Ordering, polling, interrupt acknowledgement, and reset sequencing are implemented in the consuming driver code, not in this header.

Direct includes found in this source tree include `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. `nbio_v7_0.c` uses the generated masks with NBIO register access helpers for memory-controller access enablement, doorbell ranges, clock gating, light sleep, interrupt control, HDP flush registers, and other NBIO programming. This particular chunk's PCI configuration-space capability fields are more likely to be consumed by platform, virtualization, diagnostics, or generated-register paths than by the narrow NBIO core functions shown in `nbio_v7_0.c`.

## State And Persistence Behavior

The header stores no software state and persists nothing on disk. The constants describe state located in NBIO/PCIe hardware registers for AMD NBIO 7.0 endpoints.

Hardware state represented by this chunk includes:

- PCI command/status state such as IO, memory, bus mastering, parity/SERR, interrupt disable, target/master abort, parity error, and capability-list presence.
- PCIe device and link state such as payload size, read request size, FLR initiation, completion timeout behavior, LTR/OBFF, link speed/width, ASPM, retrain/link disable, common clock, link bandwidth interrupts/status, and lane equalization controls.
- Interrupt capability state for MSI and MSI-X, including enable bits, message address/data, function mask, per-vector mask/pending bits, table offsets, and pending bit array offsets.
- AER state for correctable and uncorrectable error status/masks/severity, ECRC generation/checking, header logs, and TLP prefix logs.
- Resource sizing and power state through BAR capability/control, power-budgeting fields, DPA substate controls, and PM capability/status/control fields.
- Isolation and address-translation state through ACS, ATS, PASID, page request, ARI, multicast, TPH, and LTR capabilities.
- SR-IOV and AMD GPU-IOV virtualization state through VF enumeration/page-size/VF BAR metadata, VF enable/count shadowing, per-VF mailbox ack/valid bits, PF mailbox status, per-VF framebuffer allocation fields, reset control, and engine scheduler dwords.

Persistence is register-specific. Configuration bits usually persist until PCI configuration rewrite, FLR, secondary bus reset, GPU reset, suspend/resume, power-gating transition, or firmware/hypervisor intervention. Status and interrupt bits are often transient or write-one-to-clear, and message/ack/valid bits can represent synchronization with firmware, PF/VF, or hypervisor logic. The generated masks do not encode access type, reset value, side effects, or ordering requirements; those must come from the hardware specification and consumer code.

## Dependencies And Integration Points

This chunk depends on AMD's generated ASIC register database and is meaningful only with matching NBIO 7.0 register address/default/SMN headers:

- `nbio_7_0_offset.h` supplies the symbolic register offsets corresponding to the register names used here.
- `nbio_7_0_default.h` supplies generated defaults for many NBIO registers.
- `nbio_7_0_smn.h` supplies SMN addresses for selected NBIO/PCIe registers.
- AMDGPU helper macros such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD` pair addresses and field constants to access hardware.

Important integration points include:

- AMDGPU SOC15 initialization and NBIO v7.0 programming paths, which include this header and rely on generated shifts/masks for NBIO field updates.
- PCIe configuration and capability handling for endpoint functions exposed by the GPU, especially device/link control, AER, MSI/MSI-X, BAR sizing, power management, and extended capability traversal.
- SR-IOV/MxGPU/GPU-IOV virtualization flows, where PF/VF layout, VF BAR sizing, mailbox status, per-VF framebuffer allocation, and engine scheduler dwords must match both hardware and hypervisor expectations.
- IOMMU and PCIe isolation features through ACS, ATS, PASID, page request, ARI, multicast, TPH, and LTR fields.
- Error handling and diagnostics, where AER status/mask/severity, header logs, TLP prefix logs, link status, and lane equalization/status fields provide post-error evidence and control bits.
- Power-management code, including SMU/PowerPlay include paths that need NBIO field definitions while coordinating PCIe, DPA, LTR, OBFF, and PM capability state.

Because this file is generated, hand edits are a maintenance hazard. Correctness depends on consistency across the offset, default, SMN, and shift/mask headers for the same ASIC generation.

## Risks And Edge Cases

The main risk is silent hardware or PCI configuration-space misprogramming. These macros are untyped integer constants; an incorrect shift or mask can compile cleanly while changing the wrong bit or corrupting neighboring fields.

High-risk areas include:

- PCIe control fields: wrong payload size, read-request size, completion timeout, relaxed ordering, no-snoop, FLR, link retrain, target speed, or ASPM-related masks can cause link instability, bad performance, device reset failures, or broken enumeration.
- Interrupt capability programming: confusing MSI and MSI-X enable, mask, pending, table offset, or PBA fields can lose interrupts, generate spurious interrupts, or point the OS at the wrong MSI-X table/PBA.
- AER handling: status, mask, and severity groups have nearly identical field names. Mixing them can hide fatal errors, over-report benign errors, clear evidence before it is sampled, or fail to unmask important link/device failures.
- Virtualization: SR-IOV and GPU-IOV fields carry PF/VF layout, mailbox handshakes, reset controls, per-VF framebuffer sizing, and scheduler data. A bad field definition can break VF enumeration, corrupt VF memory partitioning, deadlock PF/VF mailbox exchange, or trigger incorrect FLR behavior.
- Address translation and isolation: ACS, ATS, PASID, page request, ARI, multicast, and TPH fields affect DMA routing and isolation. Incorrect masks can weaken peer-to-peer isolation, break IOMMU translation, or make PASID/page-request state inconsistent with the OS.
- Power management: DPA, power-budget, LTR, OBFF, and PM state fields influence latency and power policy. Misprogramming can cause unexpected wake behavior, performance cliffs, or link/power-state transition failures.
- Repetitive generated blocks: EPF1 and EPF2 contain many similarly named register families with endpoint-specific prefixes. Copying an EPF1 macro into an EPF2 path, or vice versa, may compile but target the wrong function's field layout.
- Chunk boundary splits: this range starts after the first EPF1 `DEVICE_CAP` shift definitions and ends before EPF2 `PCIE_ARI_CNTL` masks. The merge lane must reconcile adjacent chunks before making complete per-register conclusions.

## Test Signals

Useful validation signals are compile-time, generated-header, and hardware-behavior oriented:

- Kernel build coverage for AMDGPU SOC15/NBIO v7.0/SMU10 code that includes this header; missing or renamed macros should fail compilation.
- Generated-register-database comparison for lines 4970-7418 against AMD's authoritative NBIO 7.0 register descriptions, including endpoint prefixes, field widths, shifts, and masks.
- PCI enumeration and configuration-space dump checks for EPF1 and EPF2, confirming vendor/device/class/header/capability pointers, PM, PCIe, MSI/MSI-X, AER, BAR, ACS, ARI, SR-IOV, and VSEC layouts decode correctly.
- Link training and PCIe performance tests that exercise target speed, negotiated width/speed, read request size, payload size, completion timeout, LTR/OBFF, ASPM, and lane equalization fields.
- Interrupt tests covering MSI/MSI-X enable/disable, vector table/PBA offsets, mask/pending behavior, GPU interrupt delivery, suspend/resume, and reset recovery.
- AER injection or fault-observation tests for correctable and uncorrectable PCIe errors, validating status capture, mask/severity behavior, header/TLP prefix logging, and driver diagnostics.
- SR-IOV/GPU-IOV tests that create/destroy VFs, validate VF counts/stride/device IDs/VF BARs/page sizes, exercise PF/VF mailbox ack/valid bits, reset PF/VF paths, and verify per-VF framebuffer allocation.
- IOMMU/virtualization isolation tests for ACS, ATS, PASID, page request, ARI, multicast, and TPH fields under DMA, peer-to-peer, and VF workloads.
- Power-management tests across D-states, runtime PM, suspend/resume, DPA substates, LTR/OBFF policy, and link power transitions.

Regression symptoms from bad constants include failed PCI enumeration, missing interrupts, AER storms or hidden AER reports, failed FLR, broken SR-IOV VF creation, VF mailbox hangs, incorrect framebuffer partitioning, link retraining failures, DMA/IOMMU faults, or unstable runtime power transitions.

## Cross-Chunk Notes

This is one chunk of the large generated `nbio_7_0_sh_mask.h` register map. The previous chunk contains the beginning of EPF1 and the start of the EPF1 `DEVICE_CAP` group whose masks appear at the top of this range. The next chunk completes EPF2 `PCIE_ARI_CNTL` and continues later EPF2 capability/register definitions. The final per-file document should treat this chunk as hardware ABI metadata and merge endpoint/function register families across chunk boundaries.

### subset-b-003071: lines 7419-9885

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 7419-9885

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register shift/mask header. It provides C preprocessor constants for bitfield extraction and update of NBIF/BIF PCI configuration-space registers, specifically the tail of `BIF_CFG_DEV0_EPF2_0_PCIE_ARI_CNTL`, the complete `BIF_CFG_DEV0_EPF3_0_*` and `BIF_CFG_DEV0_EPF4_0_*` register families, and the beginning of `BIF_CFG_DEV0_EPF5_0_*` through `PCIE_UNCORR_ERR_SEVERITY`.

The header is data-like hardware description, not executable logic. Its purpose is to let AMDGPU NBIO code address individual PCIe configuration fields by symbolic names instead of hand-coded shifts and masks. Consumers pair these `__SHIFT` and `__MASK` constants with register addresses from adjacent generated headers and with AMDGPU register access helpers to program or inspect GPU endpoint functions.

## Register Families Covered

The opening lines finish the EPF2 ARI control register masks for `ARI_MFVC_FUNC_GROUPS_EN`, `ARI_ACS_FUNC_GROUPS_EN`, and `ARI_FUNCTION_GROUP`. The main body then declares the address block `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`, followed by a full PCI configuration layout for endpoint function 3. The same generated layout repeats for endpoint function 4 in `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`.

For EPF3 and EPF4, the chunk covers conventional PCI header fields such as vendor/device ID, command/status, revision and class codes, cache line/latency/header/BIST, BAR1 through BAR6, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. It then covers common and extended PCIe capability structures: vendor capability list, power management capability/status, serial bus release number, frame length adjustment, DBESL/DBESLD, PCIe capability/list, device/link capability/control/status including version 2 forms, MSI, MSI-X, SATA capability and indexed data port, vendor-specific enhanced capability, advanced error reporting, BAR enhanced capability, power budgeting, dynamic power allocation, access control services, and ARI.

The EPF5 section begins another copy of the same endpoint-function layout. In this chunk it reaches from identity/header/BAR/capability fields through MSI/MSI-X, SATA, vendor-specific capability, AER enhanced capability list, uncorrectable error status/mask, and uncorrectable error severity. The next chunk continues EPF5 with correctable AER and later capability blocks.

## Important APIs, Types, And Constants

There are no functions, structs, enums, or runtime APIs in this slice. The externally consumed interface is the macro naming convention:

- `BIF_CFG_DEV0_EPF{N}_0_<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position of a field.
- `BIF_CFG_DEV0_EPF{N}_0_<REGISTER>__<FIELD>_MASK` gives the unshifted register mask for that field.
- `EPF3`, `EPF4`, and `EPF5` distinguish logical PCI endpoint functions under device 0; the repeated register names intentionally represent separate hardware function configuration spaces.

Notable field groups include PCI command bits (`IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `SERR_EN`, `INT_DIS`), status/error bits (`MASTER_DATA_PARITY_ERROR`, target/master aborts, system error, parity error), BAR masks (`BASE_ADDR` over full 32-bit BAR registers), MSI/MSI-X routing fields (`MSI_EN`, `MME`, message address/data, mask/pending, table/PBA BIR and offsets), power management fields (`POWER_STATE`, `PME_EN`, `PME_STATUS`, data select/scale), and PCIe link/device control fields (`MAX_PAYLOAD_SIZE`, `MAX_READ_REQUEST_SIZE`, relaxed ordering, no-snoop, link speed/width, ASPM, retraining, bandwidth notifications).

The AER groups are particularly important for diagnosis and containment. The uncorrectable status/mask/severity fields include DLP, surprise down, poisoned TLP, flow control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable error, MC blocked TLP, AtomicOp egress blocked, and TLP prefix blocked errors. Correct interpretation requires using the status, mask, and severity registers together.

## Control Flow

This chunk has no direct control flow. It participates in control flow indirectly when AMDGPU code reads a hardware register, isolates fields with these masks, or constructs writes by shifting values into the bit positions defined here. Typical generated-header use is a read/modify/write pattern: read a register value, clear a `*_MASK`, OR in `(value << *_SHIFT) & *_MASK`, then write the register back.

Because these macros describe hardware layout, ordering in the file follows the register map rather than program execution. The EPF3, EPF4, and EPF5 blocks repeat because each endpoint function exposes the same or nearly same PCIe capability chain and configuration fields.

## State And Persistence Behavior

The header itself has no mutable software state and persists nothing. The state it describes lives in GPU NBIO/BIF PCI configuration registers. Some fields are software-controlled configuration state, such as PCI command enables, interrupt disable, MSI/MSI-X enable/masks, power-management controls, ACS controls, ARI controls, BAR controls, and DPA controls. Other fields are hardware-reported capability or status state, such as vendor/device IDs, link status, error status, and capability pointers.

Persistence depends on hardware reset and PCIe configuration behavior, not this file. Driver code using these definitions must treat many status fields as hardware-latched or write-one-to-clear according to the underlying PCIe/AER specification and ASIC register documentation. Mask constants alone do not encode access type, reset value, side effects, or required sequencing.

## Dependencies And Integration Points

This file is included by AMDGPU NBIO and register-access code in the Ceph-client Linux kernel source mirror. It is one member of a generated register family: address headers provide register offsets, this `*_sh_mask.h` file provides bit positions and masks, and driver C code combines both with AMDGPU helpers for MMIO or indirect register access.

The constants align with PCI/PCIe architectural concepts used elsewhere in the kernel: standard PCI config header fields, PCI power management, PCI Express capability, MSI and MSI-X capabilities, SATA capability, PCIe extended capabilities, AER, ACS, ARI, power budgeting, and dynamic power allocation. Integration code must also coordinate with the Linux PCI core, interrupt setup, runtime power management, GPU reset flows, error handling, SR-IOV or multi-function exposure if present, and any ASIC-specific NBIO access methods.

## Risks And Edge Cases

The highest risk is generated-register drift. If a shift or mask does not match the NBIO 7.0 hardware specification, downstream code may silently program the wrong bit, clear reserved bits, fail to enable a device function, mis-handle interrupts, or misclassify PCIe errors. Repeated EPF blocks make copy/paste or generation-template errors hard to spot manually because EPF3 and EPF4 are expected to look almost identical while still naming separate function spaces.

Boundary fields need special care. Full-width masks such as `0xFFFFFFFFL` are used for BARs, MSI addresses, IDP data, and log registers, while small-width fields share registers with reserved bits. Any write path should preserve reserved fields unless the hardware documentation explicitly allows full-register writes. AER status/mask/severity naming also invites mistakes: using a status mask constant against the severity register may compile and appear plausible because the bit positions are often the same, but it changes the semantic target.

Chunk boundaries are another review risk. This slice starts mid-EPF2 and ends mid-EPF5, so file-level reasoning must be reconciled with adjacent chunks before drawing conclusions about all endpoint functions. The EPF5 AER correctable status/mask and later BAR/power/ACS/ARI blocks are outside this chunk.

## Test Signals

There are no unit tests for these macros in this header. Useful validation signals are compile-time and hardware/driver behavior:

- Full kernel or AMDGPU builds catch missing, duplicated, or malformed macro names after generated-header changes.
- Register programming tests or bring-up logs should confirm PCI command enables, BAR programming, MSI/MSI-X setup, power-management transitions, and link/device control values are written to the intended fields.
- PCIe AER injection or real error telemetry can validate that uncorrectable status, mask, and severity bits decode consistently with Linux PCIe error handling.
- Runtime checks through PCI config dumps, debugfs, register dumps, or ASIC validation tools can compare decoded EPF3/EPF4/EPF5 values against expected hardware capability chains.
- Static review should compare this generated output against the authoritative NBIO 7.0 register database, especially around repeated EPF blocks, reserved masks, and the chunk boundaries at EPF2 ARI and EPF5 AER.

### subset-b-003072: lines 9886-12358

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 9886-12358

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 shift/mask header. It describes bitfield geometry for PCI/PCIe configuration-space registers exposed by the NBIO/BIF configuration decoder, primarily for `BIF_CFG_DEV0_EPF6_0`, `BIF_CFG_DEV0_EPF7_0`, and the beginning of `BIF_CFG_DEV1_EPF0_0`. The chunk also contains the tail of `BIF_CFG_DEV0_EPF5_0` PCIe advanced error reporting and extended capability definitions.

The file is hardware metadata rather than executable code. Each field is exported as a preprocessor pair:

- `<REGISTER>__<FIELD>__SHIFT`: the bit offset for the field.
- `<REGISTER>__<FIELD>_MASK`: the already-shifted mask for the field.

The range contains 2,131 `#define` entries over 336 commented blocks. There are 1,065 `__SHIFT` definitions and 1,066 `_MASK` definitions. The one-mask imbalance is intentional for this line range: it starts at the last four masks for `BIF_CFG_DEV0_EPF5_0_PCIE_UNCORR_ERR_SEVERITY`, whose matching shifts are in the previous chunk. The range ends at line 12358 in the middle of `BIF_CFG_DEV1_EPF0_0_DEVICE_CNTL2`; the last three masks for `LTR_EN`, `OBFF_EN`, and `END_END_TLP_PREFIX_BLOCKING` are in the next chunk.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or typedefs in this chunk. Its API is the generated macro namespace consumed by AMDGPU register access helpers.

The main register groups are:

- `BIF_CFG_DEV0_EPF5_0_PCIE_*`: the tail of endpoint/function 5 PCIe advanced error reporting and extended capabilities. The chunk begins with uncorrectable-error severity masks for internal errors, memory-controller blocked TLPs, AtomicOp egress blocking, and TLP prefix blocking. It then covers correctable error status/mask bits, advanced error capability/control, TLP header and prefix logs, BAR enhanced capability controls for BAR1 through BAR6, power-budget capability/data fields, dynamic power allocation (`DPA`) fields, access control services (`ACS`) capability/control, and alternative routing-ID interpretation (`ARI`) capability/control.
- `BIF_CFG_DEV0_EPF6_0_*`: a complete PCI configuration-space field set for device 0, endpoint/function 6. It includes vendor/device IDs, PCI command/status, revision/class/header/BIST fields, BAR1-BAR6, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, vendor capability, power-management capability/status, USB-style `SBRN`, `FLADJ`, `DBESL_DBESLD`, PCIe capability and link/device controls, MSI/MSI-X capability tables, SATA capability/index/data fields, vendor-specific enhanced capability fields, PCIe AER status/mask/severity/log fields, BAR enhanced capability controls, power budget, DPA, ACS, and ARI.
- `BIF_CFG_DEV0_EPF7_0_*`: a second complete PCI configuration-space field set for device 0, endpoint/function 7. Its layout mirrors EPF6 in this chunk: identity, command/status, BARs, power management, PCIe device/link capability and control, MSI/MSI-X, SATA, vendor-specific extended capability, AER, BAR enhanced capability, power budget, DPA, ACS, and ARI.
- `BIF_CFG_DEV1_EPF0_0_*`: the beginning of device 1, endpoint/function 0 configuration-space definitions. This chunk covers identity, PCI command/status, class/header/BIST, BARs, adapter ID, ROM base, capability pointer, interrupt metadata, vendor and power-management capabilities, PCIe capability, device/link capability and control, device/link status, Device Capability 2, and most of Device Control 2.

Important field families include:

- PCI command and status bits: `IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `SERR_EN`, `INT_DIS`, target/master abort state, parity/system-error state, capability-list presence, and interrupt status.
- BAR and ROM mapping fields: `BASE_ADDR` for BAR1-BAR6 and ROM base, plus enhanced BAR capability/control fields such as `BAR_SIZE_SUPPORTED`, `BAR_INDEX`, `BAR_TOTAL_NUM`, and `BAR_SIZE`.
- PCIe device/link controls: max payload/read-request sizes, relaxed ordering, no-snoop, extended tag, FLR initiation, link disable/retrain, common clock, extended sync, clock power management, hardware autonomous width/speed disable, and bandwidth interrupt enables/status.
- PCIe Device Capability 2 and Device Control 2 fields: completion timeout support/value/disable, ARI forwarding, AtomicOp request/routing/completion support, ID-based ordering request/completion enables, LTR, OBFF, TPH completer support, extended format, end-to-end TLP prefix support/blocking, and max TLP prefixes.
- MSI/MSI-X fields for EPF6 and EPF7: capability IDs, message control, address/data registers, per-vector masking, pending bits, table BIR/offset, and PBA BIR/offset.
- Advanced Error Reporting fields: uncorrectable error status/mask/severity for DLP, surprise down, poisoned TLP, flow control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, memory-controller blocked TLP, AtomicOp egress block, and TLP prefix block. Correctable error fields include receiver error, bad TLP/DLLP, replay rollover/timeout, advisory nonfatal, correctable internal error, and header-log overflow.
- Error log and extended capability fields: AER header logs, TLP prefix logs, first-error pointer, ECRC generation/check capabilities and enables, multi-header receive controls, and TLP prefix log presence.
- Power and topology fields: power-management capability/status/control, PCIe power-budget data selection/data/capability, dynamic power allocation substates and transition latency, ACS source validation/translation/blocking/redirect/completion controls, and ARI next-function/function-group controls.
- SATA and vendor-specific fields on EPF6/EPF7: `SATA_CAP_0`, `SATA_CAP_1`, indirect index/data pairs, vendor-specific capability ID/version/next-pointer/header, and two vendor-specific payload registers.

These macros are normally used with address macros from `nbio_7_0_offset.h`, defaults from `nbio_7_0_default.h`, and AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and indexed PCIe/NBIO accessors.

## Control Flow and Runtime Behavior

This chunk has no direct control flow. Inclusion of the header only makes constants available for compile-time expansion. Runtime behavior occurs in AMDGPU code that reads a register, extracts a field with its mask and shift, or modifies a field in a read/modify/write sequence.

The represented hardware behavior is PCIe configuration and capability behavior. Device/function identity and class fields are read by PCI enumeration and driver bring-up. Command/status fields govern whether the function accepts I/O, memory, and bus-mastering transactions and report legacy PCI error state. BAR and ROM fields represent address apertures advertised to the PCI core or internally decoded by NBIO. Capability-list and enhanced-capability next-pointer fields define how software walks the PCI/PCIe capability chains.

PCIe link and device fields participate in link configuration and error recovery. `DEVICE_CNTL` and `LINK_CNTL` settings can change payload size, read-request size, ordering behavior, FLR, link retraining, common clock configuration, clock power management, and bandwidth notifications. The matching `DEVICE_STATUS`, `LINK_STATUS`, `DEVICE_CAP2`, and `LINK_CAP` fields provide readback for negotiated link width/speed, training state, data-link active state, pending transactions, and optional PCIe features.

The AER groups define how hardware reports and classifies PCIe errors. Status registers latch error causes, mask registers suppress selected reporting, severity registers classify uncorrectable conditions as fatal or nonfatal, and log registers capture TLP headers or prefixes associated with faults. Driver-visible error handling depends on these bit positions being correct because a single wrong shift can misclassify link errors or hide actionable AER state.

MSI/MSI-X fields describe interrupt-message capability layout for EPF6 and EPF7. Message-control bits advertise 64-bit address support, per-vector masking, enabled vectors, table size, and MSI-X enable/function-mask state. Table and PBA fields carry BIR and offset values used to locate MSI-X resources.

Power-management, DPA, ACS, and ARI fields represent optional PCIe capabilities. Power-management control selects D-states and PME behavior. DPA fields describe substate count, transition latency, power-allocation scaling, selected substate, and enable/status. ACS bits determine request validation, peer-to-peer redirect/blocking, upstream forwarding, egress control, and direct translated peer-to-peer support. ARI bits expose next-function and function-group routing controls.

## State and Persistence

The header itself owns no state, allocates no memory, performs no I/O, and persists nothing. The state described by these macros lives in NBIO/PCIe hardware registers and in any software state that caches or interprets those registers.

State categories in this chunk include:

- Configuration state: PCI command enables, BAR/ROM address fields, MSI/MSI-X enables and table/PBA locations, PCIe device/link controls, Device Control 2 settings, power-management state, DPA enable/substate controls, ACS controls, and ARI forwarding/group controls.
- Capability/read-only identity state: vendor/device IDs, revision/class codes, header type, BIST capability, subsystem IDs, capability IDs, capability versions, capability next pointers, supported link speed/width, supported payload/read-request features, and optional PCIe feature support bits.
- Runtime status state: PCI status bits, interrupt status, PMI/PME status and data, device error status, link training and bandwidth status, data-link active state, AER correctable/uncorrectable status, first-error pointer, TLP header/prefix logs, DPA status, and MSI pending bits.
- Error-classification and masking state: AER uncorrectable masks, correctable masks, and severity fields. These settings determine which hardware errors become visible to operating-system AER handling and whether uncorrectable errors are reported as fatal.
- Reserved or opaque fields: several capability and status registers include reserved masks. The generated layout documents bit occupation, but runtime code should generally preserve reserved bits unless the hardware specification or firmware flow requires a specific value.

Reset values and persistence across GPU reset, function-level reset, suspend/resume, and power-gating are not encoded here. They come from ASIC defaults, firmware initialization, PCIe reset semantics, and companion `nbio_7_0_default.h` definitions. A wrong generated mask persists as a software ABI problem: every compiled caller using the macro will read or write the wrong hardware bits until the header is regenerated or corrected.

## Dependencies and Integration Points

Direct companion generated files are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`, which provides matching register address macros such as `cfgBIF_CFG_DEV0_EPF6_0_VENDOR_ID`, `cfgBIF_CFG_DEV0_EPF6_0_PCIE_UNCORR_ERR_STATUS`, `cfgBIF_CFG_DEV0_EPF7_0_VENDOR_ID`, and `cfgBIF_CFG_DEV1_EPF0_0_VENDOR_ID`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h`, which provides reset/default macros for the same generated register namespace.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h`, which is included with this header by NBIO v7.0 driver code for SMN-level register access.

In-tree consumers of `nbio_7_0_sh_mask.h` include:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, the main NBIO v7.0 implementation. It includes the offset/default/shift-mask headers and uses SOC15 register helpers for NBIO programming, including read/modify/write field operations.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c`, which includes the same generated NBIO v7.0 mask header as part of SOC15 ASIC integration.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`, which includes the header through the power-management stack.

This exact chunk is most relevant to PCIe enumeration, NBIO function configuration, SR-IOV or multi-function exposure, PCIe error handling, interrupt capability setup, link management, power management, ACS/ARI routing, and low-level ASIC bring-up. Because the chunk covers endpoint/function replicas, name alignment across EPF5, EPF6, EPF7, and DEV1/EPF0 is an important integration contract.

## Risks

- Generated-header drift is the primary risk. If any `_MASK` or `__SHIFT` differs from the ASIC register database, all users compile successfully but manipulate the wrong bit positions.
- The chunk starts and ends inside register blocks. The first four `EPF5` severity masks depend on shifts in the prior chunk, and the `DEV1_EPF0_DEVICE_CNTL2` block is missing its final three masks until the next chunk. Whole-file reconciliation must join adjacent chunks before pair-completeness checks.
- PCIe AER bit errors have high diagnostic impact. A wrong status, mask, or severity macro can hide correctable errors, misreport fatal/nonfatal state, or make captured TLP header/prefix logs appear unrelated to the actual fault.
- PCI command, BAR, ROM, and bus-mastering masks affect address decoding and DMA enablement. Incorrect use can break enumeration, expose the wrong aperture, or leave a function unable to access memory.
- Device/link control masks are sequencing-sensitive. Bad shifts for FLR, retrain, common-clock configuration, payload size, read-request size, LTR, OBFF, ARI, AtomicOp, or TLP-prefix controls can cause intermittent link failures or interoperability issues that only appear on specific platforms or switches.
- MSI/MSI-X field errors can misplace table or PBA resources or leave interrupts masked/enabled incorrectly, producing lost interrupts or spurious interrupt behavior.
- ACS and ARI fields affect request routing and isolation. Incorrect masks can weaken peer-to-peer isolation, break virtual function/function-group discovery, or route completions through the wrong path.
- Several blocks are duplicated across EPF6 and EPF7. Copy/generation skew between functions may not be noticed by builds because the macro names remain valid.
- Reserved fields should not be used as ordinary writable controls. Callers assembling raw register values without preserving reserved bits can trigger undocumented hardware behavior.

## Test and Validation Signals

Useful validation combines generated-header consistency, build coverage, and hardware behavior checks:

- Build AMDGPU paths that include `nbio_7_0_sh_mask.h`, especially `nbio_v7_0.c`, `soc15.c`, and the SMU10 PowerPlay include path, to catch syntax or missing-name regressions.
- Run static checks over the complete `nbio_7_0_sh_mask.h` file, not just this chunk, to verify every field has both `__SHIFT` and `_MASK`, masks are compatible with shifts, and masks are contiguous for ordinary scalar fields.
- Cross-check register names against `nbio_7_0_offset.h` and `nbio_7_0_default.h` so each `BIF_CFG_DEV0_EPF6_0_*`, `BIF_CFG_DEV0_EPF7_0_*`, and `BIF_CFG_DEV1_EPF0_0_*` field block has a matching address/default where expected.
- Compare EPF6 and EPF7 duplicated layouts mechanically to detect unintended field or mask drift between endpoint functions.
- Exercise PCIe enumeration and configuration on NBIO 7.0 hardware: BAR sizing, ROM base handling, bus mastering, memory access enablement, FLR, payload/read-request sizing, and link retraining.
- Validate interrupt paths that depend on these capability layouts by testing MSI and MSI-X enable/disable, vector masking, pending bits, and table/PBA decoding for the affected functions.
- Trigger or inspect PCIe AER paths where available: correctable errors, completion timeout, unsupported request, ECRC, malformed TLP, ACS violation, and header/prefix log capture.
- Exercise suspend/resume, GPU reset, runtime power management, and SR-IOV or multi-function configurations if supported, because these flows stress power-management, DPA, ACS, ARI, and function-level reset fields.

### subset-b-003073: lines 12359-14814

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 12359-14814

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, enums, variables, branches, loops, allocations, locks, direct MMIO accesses, or runtime side effects in this range.

The assigned range covers 2,456 source lines and 2,132 `#define` entries: 1,065 `__SHIFT` constants and 1,067 `_MASK` constants. The imbalance is caused by artificial chunk boundaries. The first three lines are mask constants for `BIF_CFG_DEV1_EPF0_0_DEVICE_CNTL2`; the matching shifts are in the previous chunk. The last line defines only the shift for `BIF_CFG_DEV1_EPF2_0_PCIE_HDR_LOG3__TLP_HDR`; its matching mask is in the next chunk.

Although the path is under a local `ceph-client` source mirror, this file is AMD GPU hardware metadata. It does not implement Ceph or distributed filesystem behavior. The chunk describes PCIe configuration-space bitfields for NBIO 7.0 device 1 endpoint functions, especially `BIF_CFG_DEV1_EPF0_0`, `BIF_CFG_DEV1_EPF1_0`, and the beginning of `BIF_CFG_DEV1_EPF2_0`.

## Purpose

The purpose of this range is to publish generated bitfield geometry for NBIO 7.0 PCIe/BIF configuration registers. Each exported field follows the generated AMD register convention:

- `<REGISTER>__<FIELD>__SHIFT`: bit offset of the field inside the register.
- `<REGISTER>__<FIELD>_MASK`: already-shifted bit mask used to isolate, preserve, clear, or compose the field.

Driver code consumes these constants with register offsets from `nbio_7_0_offset.h`, reset/default values from `nbio_7_0_default.h`, and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, and SOC15/NBIO access wrappers. This header has no policy by itself; it is the software contract that tells consumers which bits correspond to PCIe capability, status, control, BAR, interrupt, power, error-reporting, and virtualization-related fields.

The chunk begins at the tail of `EPF0_0` PCIe device control 2, then completes many `EPF0_0` PCIe capability blocks, includes a complete generated `EPF1_0` configuration-space block, and starts the `EPF2_0` block through early AER header-log fields. The `EPF` naming indicates endpoint function instances under `BIF_CFG_DEV1`, so the same PCIe capability structures are repeated with function-specific macro prefixes.

## Important Macro Families

The opening `BIF_CFG_DEV1_EPF0_0` portion covers PCIe device/link capability continuation and extended capability metadata for endpoint function 0. It starts with `DEVICE_CNTL2` masks for latency tolerance reporting, optimized buffer flush/fill, and TLP prefix blocking. It then covers `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`, including supported link speed, crosslink support, target link speed, compliance entry, autonomous speed disable, de-emphasis, transmit margin, equalization completion, equalization phase success, and link equalization request bits.

The MSI and MSI-X sections appear for each function. `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_PENDING`, and their 64-bit variants describe MSI capability IDs, next pointers, enable bits, vector count/capability fields, 64-bit support, per-vector masking, message address/data fields, pending state, and mask bitmaps. `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA` describe MSI-X table size, function mask, MSI-X enable, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.

The SATA capability and IDP sections (`SATA_CAP_0`, `SATA_CAP_1`, `SATA_IDP_INDEX`, `SATA_IDP_DATA`) expose generated bit layouts for the SATA capability header, BAR location/offset, indirect index, and indirect data fields. These are hardware configuration metadata, not a SATA driver implementation in this file.

Vendor-specific and VC capability blocks include `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, `PCIE_VENDOR_SPECIFIC1`, `PCIE_VENDOR_SPECIFIC2`, `PCIE_VC_ENH_CAP_LIST`, `PCIE_PORT_VC_CAP_REG1`, `PCIE_PORT_VC_CAP_REG2`, `PCIE_PORT_VC_CNTL`, `PCIE_PORT_VC_STATUS`, `PCIE_VC0_RESOURCE_*`, and `PCIE_VC1_RESOURCE_*`. These define enhanced-capability headers, VSEC IDs/revisions/lengths, scratch fields, virtual-channel counts, arbitration capabilities, arbitration table controls/status, TC/VC maps, reject-snoop controls, maximum time-slot or port arbitration table offset fields, and VC negotiation/load status.

The AER blocks are central to PCIe error handling. `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0` through `PCIE_HDR_LOG3`, and `PCIE_TLP_PREFIX_LOG0` through `PCIE_TLP_PREFIX_LOG3` define bits for data-link protocol errors, surprise down, poisoned TLP, flow control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal errors, blocked TLPs, atomic-op egress blocking, TLP prefix blocking, correctable receiver/bad TLP/bad DLLP/replay/advisory errors, ECRC generation/check controls, first-error pointer, multi-header logging, and captured TLP headers/prefixes.

The BAR enhanced capability blocks (`PCIE_BAR_ENH_CAP_LIST`, `PCIE_BAR1_CAP` through `PCIE_BAR6_CAP`, and `PCIE_BAR1_CNTL` through `PCIE_BAR6_CNTL`) describe BAR size support, BAR index, total BAR count, and selected BAR size fields. These macros are relevant to resource sizing and function configuration, but actual PCI resource allocation and mapping behavior lives in PCI core and AMDGPU runtime code.

Power-related capability metadata includes `PCIE_PWR_BUDGET_ENH_CAP_LIST`, `PCIE_PWR_BUDGET_DATA_SELECT`, `PCIE_PWR_BUDGET_DATA`, `PCIE_PWR_BUDGET_CAP`, and the DPA blocks `PCIE_DPA_ENH_CAP_LIST`, `PCIE_DPA_CAP`, `PCIE_DPA_LATENCY_INDICATOR`, `PCIE_DPA_STATUS`, `PCIE_DPA_CNTL`, and `PCIE_DPA_SUBSTATE_PWR_ALLOC_0` through `_7`. These fields describe power budget table selection, base power, data scale, PM/substate/type values, system-allocated power, DPA substate count, transition latency units/values, power allocation scale, substate status/control, and per-substate power allocation bytes.

The secondary PCIe capability and lane equalization blocks are present in `EPF0_0`: `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`. They define perform-equalization, lane error status, downstream/upstream port transmitter preset fields, and lane-specific receiver preset hints. These macros are relevant to Gen3+ link equalization diagnostics and training control surfaces.

The ACS, LTR, and ARI blocks describe isolation, latency, and alternative routing capabilities. `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` expose source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress-vector-size fields. `PCIE_LTR_ENH_CAP_LIST` and `PCIE_LTR_CAP` define latency tolerance reporting maximum snoop and no-snoop latency fields. `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL` define ARI function group capabilities, next function number, and function group controls.

The `BIF_CFG_DEV1_EPF1_0` block begins after the `addressBlock: nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp` comment. It contains a complete generated endpoint function 1 PCI config-space definition in this range: vendor/device IDs, command/status, revision and class-code fields, cache-line/latency/header/BIST fields, base address registers 1 through 6, adapter ID, ROM base address, capability pointer, interrupt line/pin, min grant and max latency, vendor capability, PMI capability/status, SBRN/FLADJ/DBESL, PCIe capability, MSI/MSI-X, SATA, vendor-specific capability, AER, BAR enhanced capability, power budget, DPA, ACS, and ARI. Unlike `EPF0_0`, this `EPF1_0` span does not include the VC, secondary capability, lane error, lane equalization, or LTR blocks inside the assigned range.

The `BIF_CFG_DEV1_EPF2_0` block starts after `addressBlock: nbio_nbif0_bif_cfg_dev1_epf2_bifcfgdecp`. This chunk includes the early function 2 PCI config-space fields through the beginning of AER header logging: vendor/device IDs, command/status, class/revision fields, BARs, adapter and ROM fields, interrupt and capability metadata, vendor and PMI capabilities, PCIe capability, device/link capability/control/status, MSI/MSI-X, SATA and vendor-specific capability, AER capability, uncorrectable/correctable error status/mask/severity, AER capability/control, and `PCIE_HDR_LOG0` through the shift-only start of `PCIE_HDR_LOG3`.

## APIs, Types, And Functions

There are no C APIs, types, functions, structs, or enums in this chunk. The public interface is the macro namespace itself.

The constants are untyped integer literals with an `L` suffix for masks and small hexadecimal constants for shifts. They are intended to be used indirectly through field helpers rather than by open-coded bit arithmetic. A typical runtime pattern in consuming code is:

1. Select an offset macro such as `cfgBIF_CFG_DEV1_EPF*_0_*` from `nbio_7_0_offset.h`.
2. Read the register through an AMDGPU register access helper.
3. Extract a field using the matching `__SHIFT` and `_MASK` macros, often via `REG_GET_FIELD`.
4. Compose a new value with a field helper or preserve unaffected bits through read/modify/write.
5. Write the resulting register value through the proper NBIO/PCIe access path if the register is writable.

Direct include users found in this source tree are `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Those include sites do not imply each macro in this chunk is referenced directly; generated register headers intentionally expose a much larger hardware database than the subset actively touched by common driver paths.

## Control Flow And Runtime Behavior

This header has no executable control flow. Including it only makes preprocessor constants available at compile time.

Runtime behavior is in AMDGPU, PCI, firmware, and hardware logic that consumes these constants. For example, PCIe capability parsing or programming may use these fields to decode link-speed support, enable or inspect MSI/MSI-X, preserve BAR configuration fields, read AER status, configure AER masks/severity, inspect header logs after link errors, handle ACS/ARI capability controls, and reason about power budget or DPA substate information. Hardware and firmware own the actual state transitions for link training, equalization, error capture, interrupt delivery, and configuration-space side effects.

The repeated `EPF0_0`, `EPF1_0`, and `EPF2_0` naming means the control path must pair a function-specific offset with the matching function-specific shift/mask macro. The macros for common PCIe structures are intentionally similar across functions, so using a mask from the wrong `EPF` prefix can look plausible in code review while targeting the wrong generated register namespace.

## State And Persistence Behavior

The header stores no software state and persists nothing. It defines bit layouts for hardware-backed PCIe configuration and extended capability registers. State represented by this range includes:

- Identification and classification state: vendor ID, device ID, revision, class code, header type, adapter ID, and capability pointers.
- Resource state: BAR address fields, ROM BAR fields, BAR enhanced-capability size and index controls.
- Interrupt state: MSI/MSI-X enable bits, table/PBA descriptors, message address/data fields, masks, pending bits, interrupt line, and interrupt pin.
- Link and capability state: PCIe device/link capability/control/status, target speed, equalization status, link control 3, lane error status, lane equalization preset fields, LTR, ARI, ACS, and VC resource fields.
- Error state: AER uncorrectable/correctable status, masks, severity bits, ECRC controls, first-error pointer, multi-header logging, TLP header logs, and TLP prefix logs.
- Power state: PME/PMI fields, power budget table values, DPA substate status/control, transition latency, and substate power allocation values.
- Reserved fields: many generated masks explicitly represent reserved bits and must be preserved according to hardware access rules.

Access permissions, reset behavior, write-one-to-clear behavior, sticky status semantics, hardware-updated fields, and firmware initialization policy are not encoded in this header. They must be taken from the hardware register specification, companion default header, PCIe specification behavior, and AMDGPU access wrappers. A mask can identify where a bit lives, but it does not say whether writing that bit is safe.

## Dependencies And Integration Points

The primary generated-header dependencies are:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`, which supplies matching register offsets such as `cfgBIF_CFG_DEV1_EPF0_0_DEVICE_CNTL2`, `cfgBIF_CFG_DEV1_EPF1_0_VENDOR_ID`, and `cfgBIF_CFG_DEV1_EPF2_0_PCIE_HDR_LOG3`.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h`, which supplies reset/default values for many of the same register names.
- Other NBIO 7.0 generated headers and SOC15 AMDGPU register access helpers, which route reads and writes through the correct NBIO, PCIe, or indexed aperture.

The main in-tree integration points are NBIO 7.0 setup and query code in `nbio_v7_0.c`, broader SOC15 initialization in `soc15.c`, and SMU10 PowerPlay include aggregation through `smu10_inc.h`. Broader runtime integration is with PCIe initialization, interrupt setup, GPU reset, suspend/resume, runtime power management, SR-IOV or multifunction exposure, link error reporting, AER diagnostics, BAR/resource programming, ACS/ARI isolation behavior, and firmware-initialized PCIe capability state.

The source-tree-aligned merge lane should reconcile this chunk with adjacent chunks for complete register-block analysis. Specifically, the preceding chunk owns the shifts for the opening `DEVICE_CNTL2` masks, and the following chunk owns the mask for the closing `EPF2_0_PCIE_HDR_LOG3` field and the rest of function 2.

## Risks And Edge Cases

- Generated-header drift is the primary risk. If a shift or mask diverges from the ASIC register database, all compiled consumers can silently read, preserve, clear, or set the wrong hardware bits.
- Chunk boundaries split complete field pairs at both ends. Any per-chunk pair-completeness check will report false positives unless adjacent chunks are considered.
- The repeated endpoint-function blocks are easy to confuse. `EPF0_0`, `EPF1_0`, and `EPF2_0` macros have many identical field names with only the function prefix changed.
- AER status and mask fields may have write-one-to-clear or sticky semantics depending on the register. Generic read/modify/write code that treats all fields as ordinary read/write controls can lose diagnostic state or fail to clear errors.
- Reserved masks are present throughout the generated layout. Code that assembles full register values without preserving reserved bits can alter undocumented hardware behavior.
- MSI/MSI-X fields interact with PCI core interrupt setup and table/PBA memory mapping. Misinterpreting table BAR indicators, offsets, mask bits, or enable bits can break interrupt delivery.
- BAR capability and control fields are resource-sensitive. Incorrect size/index interpretation can conflict with PCI resource allocation or expose wrong aperture assumptions to the driver.
- ACS and ARI fields affect isolation, routing, and multifunction enumeration behavior. Incorrect masks can affect peer-to-peer behavior, virtualization, IOMMU expectations, or function discovery.
- Link control/equalization and lane status fields are timing and hardware-state dependent. Bad decoding may appear only under specific link speeds, widths, boards, hot reset, resume, or error-recovery paths.
- Power budget and DPA fields are policy inputs rather than standalone behavior. Incorrect decoding may lead to bad power reporting or substate control decisions without an obvious local failure.

## Test And Validation Signals

Useful validation is mostly generated-header consistency plus hardware integration testing:

- Build AMDGPU with NBIO 7.0, SOC15, SMU10/PowerPlay, PCIe, MSI/MSI-X, AER, and virtualization-relevant options enabled to catch missing or renamed macros at compile time.
- Cross-check every complete register block in this chunk against `nbio_7_0_offset.h` and `nbio_7_0_default.h` for matching names, ordering, and default coverage.
- Run a generated-header consistency script that verifies complete `__SHIFT` and `_MASK` pairs, contiguous masks where expected, and sane field widths after accounting for the split first and last fields.
- Compare repeated `EPF0_0`, `EPF1_0`, and `EPF2_0` common PCIe capability layouts to detect accidental generation skew between endpoint functions.
- On NBIO 7.0 hardware, exercise PCIe link bring-up, speed/width negotiation, link retraining, hot/warm GPU reset, suspend/resume, runtime power management, and AER error capture while checking decoded link, equalization, and error status.
- Validate MSI and MSI-X interrupt setup paths, including vector count, masking, pending bits, table/PBA offsets, and 64-bit message address/data behavior.
- Validate BAR/resource reporting and any BAR enhanced-capability handling against PCI enumeration and AMDGPU aperture setup.
- Exercise ACS/ARI and multifunction or SR-IOV-like paths where supported to confirm function routing and isolation-related capability fields decode as expected.
- Check AER logs after induced or platform-reported PCIe errors to ensure uncorrectable/correctable status, severity, header log, and TLP prefix log fields are decoded with the intended masks.
- For generated-header updates, compare this chunk against the ASIC register source database rather than manually editing values in place.

## Chunk Notes

- Lines 12359-12361 finish `BIF_CFG_DEV1_EPF0_0_DEVICE_CNTL2` masks from the previous chunk.
- Lines 12362-13206 cover the rest of the visible `BIF_CFG_DEV1_EPF0_0` capability set in this chunk: link/device capability continuation, MSI/MSI-X, SATA, vendor-specific, VC, AER, BAR, power budget, DPA, secondary PCIe, lane equalization, ACS, LTR, and ARI.
- Lines 13207-14120 cover the complete visible `BIF_CFG_DEV1_EPF1_0` address block, from vendor/device ID through ARI control.
- Lines 14121-14814 begin `BIF_CFG_DEV1_EPF2_0`, from vendor/device ID through `PCIE_HDR_LOG3__TLP_HDR__SHIFT`.
- The matching `BIF_CFG_DEV1_EPF2_0_PCIE_HDR_LOG3__TLP_HDR_MASK` is outside the assigned range and should be reconciled by the adjacent chunk or final per-file merge.

### subset-b-003074: lines 14815-17235

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 14815-17235

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 7.0 register mask header. It starts in the tail of the `BIF_CFG_DEV1_EPF2_0` endpoint-function PCIe Advanced Error Reporting log area and continues through endpoint-function enhanced capability fields for BAR sizing, power budget, dynamic power allocation, ACS, and ARI. The range then enters the `nbio_pcie0_bifplr0_cfgdecp` address block and defines most of the `BIFPLR0_0` root-port/bridge PCI configuration bitfields, including base PCI bridge header fields, PCI power management, PCIe capability, link/slot/root controls, MSI and vendor-specific capabilities, virtual channels, device serial number, AER, secondary PCIe capability, lane equalization, ACS, multicast, L1 PM substates, DPC, RP PIO logging, and ESM capability fields. The final portion starts `nbio_pcie0_bifplr1_cfgdecp` and covers the beginning of the matching `BIFPLR1_0` root-port bridge definitions through the first `SLOT_CAP` fields.

The file is a generated hardware register bitfield contract. This chunk contains preprocessor constants only: no functions, structs, variables, storage allocation, or executable control flow are defined here.

## Purpose

The purpose of this header section is to provide the bit-level ABI used by AMDGPU code when reading, composing, or decoding NBIO/PCIe configuration registers for NBIO 7.0 hardware. Every register field is represented in the conventional AMD register-header form:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or compose the field.

The sibling NBIO offset header supplies register addresses; this `*_sh_mask.h` file supplies the field positions and masks for those addresses. Driver code typically consumes these definitions through register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, `WREG32`, SOC15 register accessors, or PCI/NBIO wrapper functions. Because the constants mirror hardware layout, their main value is stable, exact register encoding rather than local algorithmic behavior.

## Important Macro Families

### Endpoint Function PCIe Extended Capabilities

The opening lines finish the `BIF_CFG_DEV1_EPF2_0_PCIE_HDR_LOG*` and `BIF_CFG_DEV1_EPF2_0_PCIE_TLP_PREFIX_LOG*` groups. These expose full 32-bit TLP header and prefix log dwords used after AER events. The fields all start at shift zero with `0xFFFFFFFFL` masks, indicating whole-register payload capture rather than packed subfields.

`BIF_CFG_DEV1_EPF2_0_PCIE_BAR_ENH_CAP_LIST` and `BAR1_CAP/CNTL` through `BAR6_CAP/CNTL` define a PCIe enhanced BAR capability block for endpoint function 2. The common fields are capability ID, version, next pointer, supported BAR size bitmap, BAR index, total BAR count, and selected BAR size. These constants matter to enumeration and resizable/enhanced BAR handling, where confusing `BAR_INDEX`, `BAR_TOTAL_NUM`, and `BAR_SIZE` encodings can expose the wrong resource aperture.

`BIF_CFG_DEV1_EPF2_0_PCIE_PWR_BUDGET_*` maps PCIe power budget capability fields. It includes data selection, base power, scale, power-management state/substate, budget type, power rail, and whether the budget is system allocated. Consumers must interpret these fields as firmware/platform-advertised capability data, not as generic power-control knobs.

`BIF_CFG_DEV1_EPF2_0_PCIE_DPA_*` maps dynamic power allocation capability fields. It defines maximum substates, transition latency units/values, power allocation scale, latency indicator bits, current substate status, substate-control enable, substate-control selection, and per-substate power allocations for substates 0 through 7. The status/control split is important: status fields report hardware-selected state, while `DPA_CNTL` fields encode software control of substate policy.

`BIF_CFG_DEV1_EPF2_0_PCIE_ACS_*` defines Access Control Services capability/control fields for source validation, translation blocking, peer-to-peer redirect, upstream forwarding, egress control, direct translated P2P, and egress vector size. `BIF_CFG_DEV1_EPF2_0_PCIE_ARI_*` follows with Alternative Routing-ID Interpretation capability/control fields, including MFVC function groups, ACS function groups, next function number, MFVC enable, ACS enable, and function group selection.

### BIFPLR0 PCI Bridge Header

The `addressBlock: nbio_pcie0_bifplr0_cfgdecp` marker introduces the first PCIe bridge/root-port configuration decoder block. `BIFPLR0_0_VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST` provide the standard PCI configuration header field layout. `COMMAND` carries I/O access, memory access, bus master, special cycle, write-and-invalidate, VGA palette snoop, parity response, wait cycle, SERR, fast back-to-back, interrupt disable, and reserved bits. `STATUS` exposes interrupt status, capability-list presence, 66 MHz capability, fast back-to-back capability, parity and abort/error status, DEVSEL timing, and detected parity.

The bridge-window registers define routing aperture fields: `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `SECONDARY_STATUS`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, and `IO_BASE_LIMIT_HI`. These encode primary/secondary/subordinate bus numbers, I/O base/limit, non-prefetchable memory base/limit, and 64-bit prefetchable memory bounds. Bugs in these bit positions can misrepresent bridge apertures and break downstream device enumeration or address routing.

`CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `IRQ_BRIDGE_CNTL`, and `EXT_BRIDGE_CNTL` complete the basic bridge area. Notable control fields include parity response, SERR, ISA/VGA routing, secondary bus reset, fast back-to-back enable, and I/O port 80 enable.

### Power Management and Core PCIe Capability

`BIFPLR0_0_PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` define the PCI Power Management capability. The fields cover capability ID/next pointer, PM capability version, PME clock, device-specific init, auxiliary current, D1/D2 support, PME support, current power state, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PM data. These fields are used when the driver or PCI core reasons about device power states, wake support, and reset expectations.

`BIFPLR0_0_PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` define the base PCI Express capability. The capability fields include device type, slot implemented, interrupt message number, maximum payload support/size, max read request size, relaxed ordering, extended tag, no-snoop, auxiliary power PM, function-level reset capability, error reporting enables, and error/transaction-pending status. These masks are central to PCIe link bring-up and error policy because they encode both advertised hardware capability and writable control bits.

`BIFPLR0_0_LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` cover negotiated link behavior: speed, width, ASPM/PM support, L0s/L1 latency, clock power management, surprise-down reporting, data-link active reporting, bandwidth notification, port number, retrain/link disable controls, common clock configuration, extended sync, autonomous width disable, link bandwidth interrupt enables, current speed/width, link training, slot clock configuration, data-link active, and bandwidth-management status.

Slot/root capability groups add hotplug and PME/error paths. `SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS` include attention button, power controller, MRL sensor, indicators, surprise/hotplug capability, slot power limit/scale, interlock, command-completed support, physical slot number, hotplug interrupt enables, indicator controls, power control, presence detect, and data-link-state change status. `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` carry SERR-on-error enables, PM interrupt enable, CRS software visibility, PME requestor ID, PME status, and pending state.

### PCIe Capability 2, MSI, SSID, Vendor, and Virtual Channels

`BIFPLR0_0_DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2` cover the second-generation PCIe capability registers. They include completion timeout support/control, ARI forwarding, atomic operation support, LTR, TPH completer support, OBFF, extended format/end-to-end prefix support, emergency power reduction, ID-based ordering, 10-bit tag support, lower SKP OS generation, link target speed, compliance mode, hardware autonomous speed disable, selectable de-emphasis, transmit margin, equalization control/status, current de-emphasis level, equalization phase success bits, retimer presence, and emergency power-reduction controls.

The MSI group defines capability-list linkage, MSI enable, multiple-message capability/enable, 64-bit address capability, per-vector masking capability, message address low/high, and message data fields. `SSID_CAP_LIST` and `SSID_CAP` define subsystem vendor/device IDs. `MSI_MAP_*` maps MSI translation capability fields and MSI mapping address low/high registers.

The vendor-specific and virtual-channel groups are higher-level PCIe extended capabilities. `PCIE_VENDOR_SPECIFIC_*` exposes capability ID/version/next pointer, vendor-specific ID/revision/length, and vendor-specific dwords. `PCIE_VC_*`, `PCIE_PORT_VC_*`, and `PCIE_VC0/VC1_RESOURCE_*` define virtual-channel count, arbitration capabilities, control/status, traffic-class to virtual-channel mapping, VC IDs, VC enable bits, negotiation status, and arbitration-table controls.

### AER, Error Logging, and Root-Port Error Reporting

`BIFPLR0_0_PCIE_DEV_SERIAL_NUM_*` exposes a 64-bit device serial number through two dwords. `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` starts the Advanced Error Reporting capability. The AER groups define uncorrectable error status, mask, and severity fields for data link protocol, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned TLP egress blocked conditions.

Correctable error status and mask fields cover receiver errors, bad TLP/DLLP, replay rollover, replay timer timeout, advisory nonfatal, internal correctable error, and header-log overflow. `PCIE_ADV_ERR_CAP_CNTL` includes first-error pointer, ECRC generation/check capabilities and enables, multi-header recording, and TLP prefix log presence. `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3` expose captured AER packet context.

Root-port specific AER registers include `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, and `PCIE_ERR_SRC_ID`. They enable reporting for correctable, nonfatal, and fatal errors; record received/multiple error state; mark first uncorrectable fatal state; report fatal/nonfatal message receipt; carry the advanced-error interrupt message number; and record source IDs. These fields are integration points for PCIe AER interrupt handling and diagnostic dumps.

### Secondary PCIe, Lane Equalization, ACS, Multicast, L1 PM, and DPC

`BIFPLR0_0_PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL` define the secondary PCIe extended capability. The per-lane equalization controls repeat the same downstream transmit preset, downstream receive preset hint, upstream transmit preset, and upstream receive preset hint fields for all 16 lanes. This regular structure is important for link-training code that must index lanes without shifting the wrong preset field.

`BIFPLR0_0_PCIE_ACS_*` mirrors the ACS capability/control pattern for the root port. `PCIE_MC_*` defines PCIe multicast capability, control, base addresses, receive masks, block-all masks, block-untranslated masks, and overlay BAR fields. These fields affect peer-to-peer isolation and multicast routing; incorrect programming can create security or routing faults.

`PCIE_L1_PM_SUB_*` maps L1 PM substates. It defines capability fields for PCI-PM L1.2, PCI-PM L1.1, ASPM L1.2, ASPM L1.1, L1 PM substate support, common-mode restore time, power-on scale/value, and control fields for L1.2/L1.1 enables, common-mode restore time, LTR L1.2 threshold, timing scale, and power-on value. These constants are tied to low-power link-state policy and resume latency.

`PCIE_DPC_*` defines Downstream Port Containment capability, control, status, and error source ID. It includes trigger capability/enable, routing support, RP extension support, poisoned TLP egress blocking support/enable, software trigger, interrupt enable/status, trigger reason/extension, RP busy state, first PIO error pointer, and source ID. DPC fields are safety-critical for isolating a failing downstream device after severe PCIe errors.

### RP PIO and ESM Diagnostics

`BIFPLR0_0_PCIE_RP_PIO_STATUS`, `MASK`, `SEVERITY`, `SYSERROR`, and `EXCEPTION` define root-port PIO error classes for configuration, I/O, and memory completions: unsupported request, completer abort, and completion timeout. `PCIE_RP_PIO_HDR_LOG0..3`, `IMPSPEC_LOG`, and `PREFIX_LOG0..3` expose captured TLP context for those failures. These are diagnostic/status fields with write/clear semantics determined by hardware and PCIe capability rules, so callers should avoid treating masks and status fields interchangeably.

`BIFPLR0_0_PCIE_ESM_*` defines the start of an ESM extended capability. It includes capability list/header fields, minimum time-in-EI value/scale, ESM Gen3/Gen4 data rate controls, an enable bit, and capability bitmaps for many supported data rates. The covered capability registers enumerate rates from 8.0 GT/s through the later ESM capability dwords before the block transitions to `BIFPLR1_0`. These definitions are part of link-speed/equalization related capability discovery rather than ordinary runtime storage.

### BIFPLR1 Opening Bridge Block

The final third of the chunk introduces `addressBlock: nbio_pcie0_bifplr1_cfgdecp` and begins a second root-port/bridge instance. The early `BIFPLR1_0` definitions mirror `BIFPLR0_0`: standard PCI bridge identity/header fields, command/status, bridge bus numbering, I/O and memory aperture fields, interrupt line/pin, bridge control, port 80 control, PM capability/status, PCIe capability, device capability/control/status, and link capability/control/status.

The chunk ends inside `BIFPLR1_0_SLOT_CAP`, after attention button, power controller, MRL sensor, and attention indicator present fields. The remainder of `BIFPLR1_0_SLOT_CAP` and subsequent `BIFPLR1_0` registers are outside this chunk and must be reconciled by adjacent chunk reports.

## Control Flow

There is no runtime control flow in this header range. The only structure is the generated ordering of register comments followed by `#define` constants. Runtime control flow appears in external AMDGPU/NBIO/PCIe code that chooses when to read or write these registers. For example, link-management paths may read link status fields before deciding whether to retrain a link, AER/DPC handlers may read status/log fields after an interrupt, and power-management paths may update PM or L1 substate controls.

The implicit access pattern for writable fields is read-modify-write: read a register value, clear a field with its mask, shift a new value by the field's `__SHIFT`, mask it, and write the resulting register value. For status and log fields, consumers generally read, decode, and sometimes clear according to hardware-defined write-one-to-clear or capability-specific semantics that are not encoded in this header.

## State and Persistence Behavior

This chunk defines names for hardware state; it does not persist anything in memory or on disk. The underlying registers represent several kinds of state:

- PCI configuration identity and capability advertisement, which are usually hardware/firmware initialized and persistent across normal driver reads until reset.
- Writable PCIe controls such as command bits, bridge windows, PM state controls, error-reporting enables, link controls, slot controls, ACS controls, VC controls, L1 substate controls, and DPC controls.
- Volatile status bits such as link training/data-link active state, slot events, PME pending, device error flags, AER correctable/uncorrectable status, DPC trigger status, RP busy, and PIO error status.
- Diagnostic capture registers such as TLP header logs, TLP prefix logs, root-port PIO logs, and error source IDs, which preserve context from hardware error events until cleared or overwritten by hardware.

Reset, bus reset, D3 transitions, function-level reset, DPC containment, or firmware reinitialization can change the backing hardware state. The macros themselves are compile-time constants and have no lifecycle.

## Dependencies and Integration Points

This header depends on consumers including the correct NBIO 7.0 ASIC register headers. It is normally paired with an offset header that names register addresses and with AMDGPU register helper macros that know how to combine `__SHIFT`/`_MASK` constants. The `BIF_CFG_DEV1_EPF2_0`, `BIFPLR0_0`, and `BIFPLR1_0` prefixes are part of the generated naming scheme and must match the hardware IP block, instance, and PCIe function/root-port layout used by the driver.

Important integration areas include:

- PCI enumeration and bridge-resource setup for command/status, bus numbering, and I/O/memory/prefetchable aperture fields.
- PCIe link management for link capability/control/status, Link Control 2/3, equalization, lane error, and ESM data-rate fields.
- Power management for PMI status/control and L1 PM substate fields.
- Error handling for AER status/mask/severity, root error command/status/source ID, DPC status/control/source ID, and RP PIO logging.
- Hotplug/root-port support for slot capability/control/status and root PME fields.
- Isolation and routing policy for ACS, multicast, virtual channels, ARI, and BAR capability fields.
- Diagnostics and debug tooling that dumps TLP header/prefix logs, PIO logs, serial number fields, device/link status, and error masks.

## Risks

The main risk is bitfield drift from hardware documentation. A wrong shift or mask can silently corrupt read-modify-write operations, decode status incorrectly, or advertise unsupported capability state. The highest-risk groups are writable controls and error/security-related fields: bridge apertures, bus-master/memory-enable bits, AER masks/severity, DPC controls, ACS controls, multicast routing, link retrain/disable bits, L1 substate controls, and per-lane equalization fields.

Generated-name similarity is another risk. Many fields repeat across `BIF_CFG_DEV1_EPF2_0`, `BIFPLR0_0`, and `BIFPLR1_0`; using a macro from the wrong prefix may compile but target the wrong register layout or port instance. The `*_MASK_MASK` naming pattern in error mask registers is intentional: the register is named `*_MASK` and the field is also named `*_MASK`. Automated scripts and human reviewers should avoid "simplifying" those names.

Whole-register log fields use `0xFFFFFFFFL` masks and shift zero. They should be handled as raw captured dwords, not as scalar values with further implied interpretation in this header. Conversely, multi-bit fields such as bridge apertures, link width/speed, equalization presets, and power budget scales require both mask and shift; testing only single-bit flags would miss off-by-one or width errors.

Status, mask, severity, and control registers often share nearly identical field names. AER and RP PIO code must not confuse status bits with mask or severity bits, since a status read/clear path has different semantics from an enable/mask update path. Some status bits may be write-one-to-clear or hardware-cleared; this header does not encode those access rules.

## Test Signals

Useful verification signals for this chunk are mostly compile-time and hardware/driver integration signals:

- Kernel/driver build coverage with this header included by AMDGPU NBIO/PCIe code, catching missing or renamed macros.
- Static checks that every field has a matching `__SHIFT` and `_MASK` pair, except where generated conventions intentionally omit one.
- Register-generation diffs against the authoritative NBIO 7.0 register database or vendor header source, especially for repeated `BIFPLR0_0`/`BIFPLR1_0` field families.
- PCIe enumeration tests on NBIO 7.0 hardware that verify bridge bus numbers, memory windows, BAR capabilities, link speed/width, MSI, PM capability, and slot/root-port capability decode correctly.
- AER/DPC fault-injection or error-observation tests that confirm uncorrectable/correctable status, masks, severity, root error status/source ID, TLP logs, DPC status, and RP PIO logs decode as expected.
- Link power-management tests covering ASPM/L1 substates and resume latency, plus link retrain/equalization tests that validate Link Control 2/3, lane error, and per-lane equalization macros.
- Security/isolation checks for ACS, ARI, multicast, and virtual-channel programming, particularly in peer-to-peer, IOMMU, and multi-function scenarios.

### subset-b-003075: lines 17236-19637

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 17236-19637

## Scope

This chunk covers 2,402 lines from the generated AMD NBIO 7.0 shift/mask header. It starts in the middle of the `BIFPLR1_0_SLOT_CAP` definition, continues through the remainder of the `BIFPLR1_0` PCIe capability and enhanced-capability register fields, switches at `// addressBlock: nbio_pcie0_bifplr2_cfgdecp`, and then covers the beginning of the `BIFPLR2_0` PCIe bridge/configuration-space field map through most of `BIFPLR2_0_PCIE_ROOT_ERR_STATUS`.

There are no C functions, structs, enums, globals, locks, allocations, branches, or direct register accesses in this range. The public surface is preprocessor symbols of the generated form:

- `<REGISTER>__<FIELD>__SHIFT`
- `<REGISTER>__<FIELD>_MASK`

The range is a register-definition fragment, not executable driver logic. It is still important because AMDGPU code and helper macros depend on these constants when decoding or composing NBIO and PCIe configuration-space register values for this ASIC generation.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 register interface. The matching generated headers provide complementary information:

- `nbio_7_0_offset.h` maps register names to MMIO/PCIE/config-space offsets.
- `nbio_7_0_default.h` provides reset/default values for many registers.
- `nbio_7_0_smn.h` provides SMN-addressed NBIO symbols.

This chunk describes PCIe root-port and bridge-facing register fields for two NBIO PCIe logical register blocks:

- `BIFPLR1_0`, mainly the latter part of its PCIe Capability and Enhanced Capability structures.
- `BIFPLR2_0`, from base PCI/PCI-to-PCI bridge configuration registers through AER root error status.

The macro names follow PCIe terminology closely: slot control/status, root control/status, Device Capabilities 2, Link Capabilities/Control/Status 2, MSI, virtual channels, advanced error reporting, link equalization, access control services, multicast, L1 PM substates, downstream port containment, root-port PIO logs, and ESM link-speed capability bitmaps. Consumers can use the generated shift/mask symbols with helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32*`, and `WREG32*` without embedding numeric bit constants in runtime code.

## Register Families Covered

The chunk begins with the tail of `BIFPLR1_0_SLOT_CAP`: power indicator, hot-plug, slot power-limit, electromechanical interlock, command-completed support, and physical slot-number fields. The first few `SLOT_CAP` shift definitions are in the previous chunk, but all `SLOT_CAP` masks are visible here.

The next `BIFPLR1_0` core PCIe capability fields include:

- `SLOT_CNTL`, `SLOT_STATUS`, `ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` for hot-plug, slot events, SERR/PME reporting, CRS software visibility, and PME requestor/status tracking.
- `DEVICE_CAP2`, `DEVICE_CNTL2`, and `DEVICE_STATUS2` for completion timeout, ARI, AtomicOp, IDO, LTR, OBFF, end-to-end TLP prefixes, and reserved status bits.
- `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` for supported/target link speeds, compliance-entry controls, de-emphasis, equalization phase status, and equalization requests.
- Reserved `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2` fields.

The chunk then covers `BIFPLR1_0` MSI and vendor/extended capabilities:

- `MSI_CAP_LIST`, `MSI_MSG_CNTL`, address low/high, and data fields for MSI programming.
- `SSID_CAP_LIST` and `SSID_CAP` for subsystem vendor and subsystem IDs.
- `MSI_MAP_CAP_LIST`, `MSI_MAP_CAP`, and MSI-map address fields.
- `PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`, `PCIE_VENDOR_SPECIFIC_HDR`, and two scratch-style vendor-specific payload registers.

The `BIFPLR1_0` PCIe enhanced capability groups in this chunk include:

- Virtual Channel (`PCIE_VC_ENH_CAP_LIST`, port VC capability/control/status, `VC0` and `VC1` resource capability/control/status).
- Device Serial Number (`PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `DW1`, `DW2`).
- Advanced Error Reporting (`PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable status/mask/severity, correctable status/mask, AER capability/control, TLP header logs, root error command/status, error source IDs, and TLP prefix logs).
- Secondary PCIe, Link Control 3, lane error status, and per-lane equalization control for lanes 0 through 15.
- Access Control Services (`ACS_CAP`, `ACS_CNTL`) for source validation, translation blocking, peer-to-peer redirect/egress, upstream forwarding, and direct translated P2P.
- Multicast capability/control/address/receive/block/overlay BAR registers.
- L1 PM Substates capability/control/control2.
- Downstream Port Containment (`DPC_CAP_LIST`, `DPC_CNTL`, `DPC_STATUS`, error source ID).
- Root Port PIO status, mask, severity, system-error, exception, header log, implementation-specific log, and prefix log registers.
- ESM capability headers/status/control and `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`, which are dense bitmaps for supported ESM data-rate points from 8.0G through 28.0G.

After the address-block transition, `BIFPLR2_0` starts at base PCI/bridge configuration fields:

- Vendor/device ID, command/status, revision/class-code fields, cache-line/latency/header/BIST fields.
- Bus-number, IO window, memory window, prefetchable window, upper-address, capability pointer, interrupt line/pin, bridge control, and extended bridge control.
- Power Management capability/status-control.
- PCIe capability, Device Capabilities/Control/Status, Link Capabilities/Control/Status, Slot Capabilities/Control/Status, Root Control/Capability/Status, Device/Link/Slot Capability 2 families, MSI, SSID, MSI map, vendor-specific, VC, serial number, and AER fields through root error status.

The final visible line is `BIFPLR2_0_PCIE_ROOT_ERR_STATUS__FATAL_ERROR_MSG_RCVD_MASK`. The `ADV_ERR_INT_MSG_NUM_MASK` field for that same register is on the next physical line and therefore belongs to the next chunk.

## Important APIs, Types, and Functions

This header segment exposes no callable APIs or C types. Its API is the generated macro namespace consumed by AMDGPU register helpers. The important contract is that each field has a matching shift and mask with a stable generated name.

Typical consumers use these symbols in patterns like:

- `REG_GET_FIELD(value, BIFPLR2_0_LINK_STATUS, NEGOTIATED_LINK_WIDTH)` to decode a field from a read register value.
- `REG_SET_FIELD(value, BIFPLR1_0_DEVICE_CNTL2, LTR_EN, 1)` to compose a read-modify-write value.
- `FIELD_MASK` constants directly when clearing, testing, or preserving specific status/control bits.

Important field groups by behavior:

- Capability IDs and next pointers (`*_CAP_LIST`, `*_ENH_CAP_LIST`) describe PCI/PCIe capability-chain layout.
- Capability registers (`*_CAP`, `*_CAP2`) advertise hardware support and should usually be treated as read-mostly hardware descriptions.
- Control registers (`*_CNTL`, `*_CNTL2`, `*_ROOT_ERR_CMD`, `*_ACS_CNTL`, `*_DPC_CNTL`) contain writable feature-enable, interrupt-enable, containment, link-control, or reporting-policy bits.
- Status registers (`*_STATUS`, `*_STATUS2`, AER status, DPC status, PIO status) report latched or live hardware state. Some status bits may be write-one-to-clear according to PCIe semantics even though this generated header does not encode access mode.
- Log registers (`*_HDR_LOG*`, `*_TLP_PREFIX_LOG*`, `*_RP_PIO_*_LOG*`) expose captured TLP headers/prefixes for error handling and diagnostics.
- Window/address registers (`MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `IO_BASE_LIMIT`, multicast address and overlay BAR fields, MSI message and mapping addresses) carry address bits and must be paired with correct size/alignment semantics from PCIe or the hardware database.

## Control Flow

There is no local control flow. The generated constants participate in external driver and platform flows:

1. AMDGPU, PCI core code, firmware-facing code, or diagnostics selects a register offset from `nbio_7_0_offset.h` or an SMN/MMIO/PCIE accessor path.
2. The caller reads a register or starts from a cached/default value.
3. The caller extracts a field using the `__SHIFT`/`_MASK` pair or composes a modified value with a helper such as `REG_SET_FIELD`.
4. For writable registers, the caller writes the value through the relevant MMIO, SOC15, PCIE, or SMN accessor.
5. PCIe/NBIO hardware consumes control bits or reports status/log bits asynchronously based on link, power, error, interrupt, and reset state.

Representative runtime flows that depend on this style of generated header include PCIe link bring-up and retraining, completion-timeout and LTR policy setup, MSI configuration, hot-plug and PME reporting, AER/DPC error handling, ACS/IOMMU isolation policy, L1 PM substate programming, GPU reset and secondary-bus reset handling, and register dumps used during hardware debug.

The file is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h` in this source tree. Direct references to every macro are not required; many generated field names are consumed only for specific ASICs, diagnostics, or conditionally compiled paths.

## State and Persistence Behavior

The header stores no software state. It names hardware-visible bits in PCIe configuration-space style registers for NBIO 7.0.

Persistence is hardware- and reset-domain-dependent:

- Capability registers are generally hardware-defined and stable across normal runtime operation, but can differ by ASIC, fuse/strap state, board wiring, firmware configuration, or PCIe port mode.
- Control registers can be programmed by BIOS/firmware, the Linux PCI core, AMDGPU, virtualization layers, or error-handling paths. Their values may need restoration after GPU reset, function-level reset, secondary bus reset, S3/S4 suspend/resume, or runtime power transitions.
- Status and error registers can be latched by hardware events. AER, DPC, root error status, PIO status, and PCI status bits may require explicit clearing with PCIe-defined write semantics.
- Log registers are transient diagnostic state. Header/TLP-prefix/PIO logs describe the transaction associated with an error and may be overwritten by later errors or cleared during recovery.
- Address/window registers define decoded IO, memory, prefetchable, MSI, and multicast regions. Incorrect persistence or restore behavior can affect reachability, interrupt delivery, peer routing, or isolation.

The chunk itself does not encode reset values, read/write permissions, write-one-to-clear behavior, volatile/live status behavior, or ownership. Those semantics must come from the PCIe specification, AMD register database, `nbio_7_0_default.h`, platform firmware policy, and the driver paths that use these fields.

## Dependencies and Integration Points

The immediate dependency is the generated NBIO 7.0 register-header set. This chunk is only useful when paired with the corresponding offset/default/SMN headers and the AMDGPU register helper macros.

Primary integration points in this source tree:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c` includes `nbio_7_0_sh_mask.h` and programs NBIO generation-specific behavior such as memory-controller access, doorbell aperture ranges, HDP remapping, clock gating, light sleep, and indirect sys-hub registers.
- `drivers/gpu/drm/amd/amdgpu/soc15.c` includes NBIO 7.0 headers as part of SOC15 ASIC initialization and common IP setup for Vega/Raven-era devices.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h` pulls NBIO 7.0 definitions into SMU10/power-management include stacks alongside MP and THM generated headers.
- Linux PCIe infrastructure can indirectly depend on the same hardware fields when AMDGPU or platform code surfaces link state, AER/DPC handling, MSI programming, bridge windows, power-management policy, and hot-plug/PME behavior.

Cross-file generated-header consistency is critical. Register names in this shift/mask header must match offsets in `nbio_7_0_offset.h`; otherwise code can compile while extracting the right field shape from the wrong register address. Default values in `nbio_7_0_default.h` should be consistent with read-only/reserved field masks and expected reset state.

## Risks and Edge Cases

- The chunk starts mid-register. `BIFPLR1_0_SLOT_CAP` is incomplete without the previous chunk, which contains the first shift definitions.
- The chunk ends mid-register. `BIFPLR2_0_PCIE_ROOT_ERR_STATUS__ADV_ERR_INT_MSG_NUM_MASK` is on the next source line and must be reconciled by the merge lane.
- Capability and control registers often share similar field names across `BIFPLR1_0` and `BIFPLR2_0`. A wrong prefix can compile but target a different PCIe port or config-decode block.
- Many fields mirror standardized PCIe bit positions. Small mask/shift mistakes can silently break Linux PCIe expectations for MSI, AER, DPC, ACS, L1 PM substates, hot-plug, or bridge-window setup.
- Status/error bits may be write-one-to-clear or otherwise side-effectful. The generated mask does not communicate access semantics, so generic read-modify-write code can accidentally clear or preserve the wrong error state.
- Reserved fields are explicitly named for some registers. Software should preserve reserved bits unless hardware documentation says otherwise.
- Address-window fields expose partial address bits and require PCIe-specified alignment. Treating mask width as the full address without applying implied low bits can produce invalid IO, memory, MSI, or multicast windows.
- ESM capability bitmaps are dense and regular. Off-by-one generation errors in data-rate bits are hard to notice in compile tests but can advertise or select unsupported link-speed/equalization behavior.
- ACS and peer-to-peer controls affect IOMMU/security isolation and GPU-to-GPU routing. Incorrect masks or restore policy can cause either lost P2P performance or unsafe peer access.
- DPC and AER controls affect recovery behavior after PCIe errors. Bad masks can suppress reporting, misclassify fatal/nonfatal errors, block poisoned TLP handling, or leave ports contained longer than expected.
- MSI and MSI-map fields affect interrupt delivery. Incorrect address/data masks can create lost or misrouted interrupts, especially across resume, reset, or virtualization transitions.

## Test Signals

Useful validation for this chunk is mostly compile-time, generated-header consistency, and hardware/PCIe behavior testing:

- Build AMDGPU configurations that include SOC15, NBIO 7.0, SMU10, AER/DPC-capable PCIe support, and power-management paths. This catches missing or renamed generated symbols.
- Run generated-register consistency checks: every register in this chunk should have matching offset entries in `nbio_7_0_offset.h`, and shift/mask pairs should agree with the authoritative AMD register database.
- Check boundary continuity with neighboring chunks: complete `BIFPLR1_0_SLOT_CAP` at the start and complete `BIFPLR2_0_PCIE_ROOT_ERR_STATUS` at the end.
- Validate PCIe enumeration on affected AMD GPUs: vendor/device IDs, class/header type, bridge windows, capability pointers, MSI capability, PCIe capability, and enhanced-capability chain should decode as expected.
- Exercise link training and retraining across supported speeds and widths; confirm `LINK_STATUS`, `LINK_STATUS2`, `LINK_CNTL2`, lane equalization, and ESM-related bits match observed link behavior.
- Test suspend/resume, GPU reset, secondary bus reset, and function reset to ensure control registers for LTR, OBFF, ACS, DPC, AER, MSI, and bridge windows are restored or intentionally reinitialized.
- Inject or observe PCIe AER/DPC events where supported and verify uncorrectable/correctable status, masks, severities, root error status, error source IDs, TLP header logs, and prefix logs decode correctly.
- Verify MSI delivery before and after reset/resume, including 64-bit MSI address and MSI-map fields where the platform uses them.
- For ACS/IOMMU-sensitive systems, verify isolation and peer-to-peer routing policy using PCIe topology tests and GPU P2P workloads.
- For power-management paths, verify L1 PM substate and LTR behavior does not regress idle power, wake latency, or link stability.

## Unresolved Cross-Chunk References

The previous chunk is needed for the first `BIFPLR1_0_SLOT_CAP` shift fields, including attention button, power controller, MRL sensor, and attention indicator presence. This chunk contains the remaining `SLOT_CAP` shifts and all `SLOT_CAP` masks.

The next chunk begins with the final mask for `BIFPLR2_0_PCIE_ROOT_ERR_STATUS` and then continues into `BIFPLR2_0_PCIE_ERR_SRC_ID`, TLP prefix logs, secondary PCIe enhanced capability, Link Control 3, lane error/equalization registers, and later `BIFPLR2_0` capability groups. The final per-file document should merge those boundaries before describing complete `BIFPLR1_0` and `BIFPLR2_0` coverage.

### subset-b-003076: lines 19638-22048

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 19638-22048

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment for PCIe bridge/root-port configuration-space registers. It contains 2,170 `#define` field-layout macros across 239 register comment blocks. There are no C functions, structs, enums, global objects, locks, allocations, branches, or executable statements in this range.

The range starts inside the `BIFPLR2_0` PCIe Advanced Error Reporting area, immediately after the `BIFPLR2_0_PCIE_ROOT_ERR_STATUS__ADV_ERR_INT_MSG_NUM_MASK` definition from the previous register block. It then finishes the tail of the `BIFPLR2_0` enhanced capability chain through Equalization Status Monitoring capabilities. The chunk also introduces the `nbio_pcie0_bifplr3_cfgdecp` address block and covers the beginning of the `BIFPLR3_0` PCI/PCIe bridge configuration register map through the first part of `BIFPLR3_0_PCIE_ESM_CAP_1`. The next chunk is required for the remaining `BIFPLR3_0_PCIE_ESM_CAP_1` masks and later ESM capability registers.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 register interface. For each register field, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the field's starting bit.
- `<REGISTER>__<FIELD>_MASK`, the field's bit mask.

The companion `nbio_7_0_offset.h` supplies matching `cfg*` offsets for these configuration-space registers. Runtime AMDGPU code combines these constants with register access helpers, `REG_GET_FIELD`/`REG_SET_FIELD`-style operations, SOC15/NBIO accessors, and PCIe/NBIO generation code. This source path is under a Ceph mirror, but the content is AMD GPU hardware metadata, not distributed-filesystem logic.

The represented hardware purpose is PCIe root-port and bridge configuration for NBIO 7.0: PCI command/status and bridge window decoding, MSI/MSI mapping, PCIe capability negotiation, advanced error reporting, access control services, multicast, L1 power-management substates, downstream port containment, root-port PIO error reporting, and equalization/status-monitoring capability discovery.

## Important Macro Families

The opening `BIFPLR2_0` portion completes a PCIe capability and enhanced-capability tail:

- AER continuation: `ERR_SRC_ID`, four `TLP_PREFIX_LOG*` registers, and the chunk-leading final `ROOT_ERR_STATUS` mask from the previous block. These fields identify correctable and fatal/nonfatal error sources and preserve logged TLP prefixes.
- Secondary PCIe and link equalization: `PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, `PCIE_LANE_ERROR_STATUS`, and `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL`. These fields expose Gen3 equalization request/control, lower SKP ordered-set generation, per-lane error status, and downstream/upstream TX/RX preset or hint nibbles.
- ACS: `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL`, covering source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, direct translated P2P, and egress-control vector sizing.
- Multicast: `PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, address/receive/block/untranslated bitmaps, and overlay BAR fields for multicast group address decoding and blocking policy.
- L1 power-management substates: `PCIE_L1_PM_SUB_CAP`, `PCIE_L1_PM_SUB_CNTL`, and `PCIE_L1_PM_SUB_CNTL2`, including L1.1/L1.2 support and enables, common-mode restore time, power-on scale/value, and T_POWER_ON.
- DPC and RP PIO: DPC capability/control/status/error-source fields plus `PCIE_RP_PIO_STATUS`, `MASK`, `SEVERITY`, `SYSERROR`, `EXCEPTION`, TLP header logs, implementation-specific log, and prefix logs. These fields classify unsupported request, completer abort, and completion-timeout errors across config, I/O, and memory spaces.
- ESM: `PCIE_ESM_CAP_LIST`, ESM headers/status/control, and `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`, where capability bits enumerate supported data-rate points from 8.0 GT/s through 28.0 GT/s in 0.1 increments across multiple registers.

The `BIFPLR3_0` portion begins a parallel bridge/root-port configuration map:

- Conventional PCI bridge config fields: vendor/device ID, command/status, revision/class, cache-line/latency/header/BIST, subordinate/secondary/primary bus numbers, I/O and memory base/limit windows, prefetchable windows, capability pointer, interrupt line/pin, bridge control, and extension bridge control.
- Power management and PCIe capabilities: PMI capability/status/control; PCIe capability, device/link/slot/root capability/control/status, and device/link/slot second-generation capability/control/status registers.
- Interrupt and identity extensions: MSI capability, message control/address/data fields, subsystem IDs, MSI map capability and address fields, vendor-specific enhanced capability headers/data, virtual-channel capability/resource controls for VC0 and VC1, and device serial number fields.
- AER for `BIFPLR3_0`: enhanced capability list, uncorrectable status/mask/severity, correctable status/mask, advanced error capability/control, header logs, root error command/status, source IDs, and TLP prefix logs.
- The same secondary PCIe, lane equalization, ACS, multicast, L1 PM substate, DPC, RP PIO, and ESM capability families seen for `BIFPLR2_0`, ending in the first half of `BIFPLR3_0_PCIE_ESM_CAP_1`.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public contract is the preprocessor macro namespace and its generated naming convention. Consumers use register names and field names to extract or update bits, while the actual address selection comes from `nbio_7_0_offset.h`.

The constants are untyped integer literals, with masks usually carrying an `L` suffix. They encode bit positions only. They do not encode access width, read/write permissions, reset values, write-one-to-clear behavior, polling rules, firmware ownership, side effects, or whether a field is legal to program in a given PCIe link state. Those semantics must come from the PCIe specification, AMD's register database, and the code path performing the hardware access.

## Control Flow

This header segment has no local control flow. Runtime flow is external:

1. NBIO, PCIe, display/resource, power-management, diagnostics, or reset code selects a `BIFPLR2_0` or `BIFPLR3_0` configuration register offset.
2. The caller reads a register, decodes fields with the generated shift/mask constants, or composes a new register value by preserving unrelated bits and inserting field values.
3. The caller writes through the AMDGPU register access path or exposes decoded values through diagnostics.
4. Hardware consumes the values as PCIe configuration state, capability reporting, link equalization state, power-management policy, error-reporting state, DPC/RP PIO status, or ESM capability data.

Typical higher-level flows include NBIO initialization, PCIe bridge capability setup, link-training/equalization observation, AER and DPC error handling, L1 substate policy programming, MSI/MSI-map setup, virtual-channel setup, suspend/resume reinitialization, GPU reset, and register dumps.

## State And Persistence Behavior

The header stores no software state. It names state held in NBIO 7.0 PCIe configuration registers. Persistence is determined by PCIe configuration-space reset semantics, GPU reset domains, function-level reset, hot/warm reset, power management transitions, firmware/SMU initialization, and any driver save/restore path.

Represented state includes bridge decode windows, command/status bits, capability-list links, MSI and MSI-map configuration, PCIe device/link/slot/root capability state, AER status/masks/severity/logs, root error reporting enables, per-lane equalization controls and status, ACS controls, multicast routing policy, L1 PM substate controls, DPC enable/status/trigger/reporting state, RP PIO error masks/severity/syserror/exception bits, and ESM support/control state.

Several fields are not passive storage. AER and DPC status bits may be latched and clear-sensitive; interrupt and root error command bits alter reporting behavior; bridge windows affect transaction routing; ACS and multicast controls affect peer-to-peer and multicast forwarding; L1 substate controls affect link power management; equalization controls interact with PCIe link training; and ESM fields expose link-rate monitoring capability and enablement. The generated masks alone are not enough to infer whether a write is safe.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.0 register header set:

- `nbio_7_0_offset.h` supplies matching `cfgBIFPLR2_0_*` and `cfgBIFPLR3_0_*` offsets for the register names in this chunk.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` naming convention for field extraction and read-modify-write updates.
- The generated values must remain synchronized with AMD's NBIO 7.0 register database and with equivalent later-generation headers, which carry closely related `BIFPLR2_0`/`BIFPLR3_0` capability maps.

Observed include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`, and display resource code that includes NBIO 7.0 offsets. The integration surface is the AMDGPU PCIe/NBIO stack: ASIC bring-up, resource discovery, bus and bridge setup, power management, error handling, diagnostics, and reset recovery.

## Risks And Edge Cases

- The chunk begins and ends mid-register family. `BIFPLR2_0_PCIE_ROOT_ERR_STATUS` starts before this range, and `BIFPLR3_0_PCIE_ESM_CAP_1` continues after it. Final file-level research must reconcile these boundaries.
- Generated shift/mask drift can compile cleanly while decoding or programming the wrong hardware bit. High-risk fields include bridge decode windows, AER clear/status bits, DPC controls, ACS controls, MSI mapping, equalization controls, and L1 substate controls.
- `BIFPLR2_0` and `BIFPLR3_0` families are highly repetitive. A copy/generator error may affect one bridge instance while neighboring instances still look correct.
- Capability-list `NEXT_PTR` fields and overlapping capability/control register offsets must match `nbio_7_0_offset.h`; otherwise capability walking or debug decode can point at the wrong structure.
- Status and clear-sensitive fields need hardware-specific handling. Treating AER, DPC, RP PIO, or bridge status bits as ordinary writable state may drop error evidence or leave stale events latched.
- Link equalization, L1 PM substate, DPC containment, and ESM enable fields are tied to PCIe link state. Writes during training, reset, or low-power transitions can cause link instability or misleading diagnostics.
- ACS, multicast, bridge windows, and MSI mapping affect transaction routing and isolation. Incorrect values can break peer-to-peer paths, DMA routing, interrupts, or virtualization/security boundaries.
- Reserved masks are present for preservation, but driver code should avoid intentionally changing reserved bits unless the hardware programming guide requires a specific sequence.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.0, SOC15, SMU10 power-management includes, and display/resource include paths; this catches missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: shift/mask non-overlap, mask width, field order, capability-list links, and matching offsets in `nbio_7_0_offset.h`.
- Validate cross-instance consistency between `BIFPLR2_0` and `BIFPLR3_0` where the register families are intended to mirror each other, while allowing legitimate differences in base offsets or conventional bridge fields.
- Runtime tests on affected AMD GPUs should cover PCIe enumeration, negotiated speed/width, Gen3 equalization, L1.1/L1.2 entry and exit, suspend/resume, warm reset, GPU reset, and error recovery.
- AER/DPC/RP PIO validation should inject or observe correctable, nonfatal, fatal, unsupported-request, completer-abort, and completion-timeout paths where supported, confirming status, mask, severity, source-ID, header-log, prefix-log, and root-error reporting behavior.
- Routing tests should verify bridge memory/I/O windows, ACS policy, multicast fields if used, MSI/MSI-map delivery, and VC resource programming.
- ESM diagnostics should confirm that data-rate capability bits, status timing fields, and enable/control fields decode consistently with hardware support and the PCIe link speeds exposed by the platform.

### subset-b-003077: lines 22049-24433

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 22049-24433

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register field header. It provides C preprocessor constants for bit shifts and bit masks used to decode or update PCIe/NBIO configuration-space registers. The range starts in the middle of `BIFPLR3_0_PCIE_ESM_CAP_1`, completes the `BIFPLR3_0_PCIE_ESM_CAP_2` through `CAP_7` field maps, defines the full `nbio_pcie0_bifplr4_cfgdecp` address block, and begins the `nbio_pcie0_bifplr5_cfgdecp` address block through `BIFPLR5_0_IRQ_BRIDGE_CNTL`.

The header has no executable code. Its purpose is to be a stable hardware contract for AMDGPU C code that uses register access helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32*`, `WREG32*`, and `SOC15_REG_OFFSET` together with matching `reg...` address definitions from the NBIO offset headers.

## Macro API Surface

Every field is represented as two macros:

- `<register>__<field>__SHIFT`: the least-significant bit position for the field.
- `<register>__<field>_MASK`: the bit mask already positioned in the register word.

The naming style is important because AMDGPU helper macros concatenate `reg` and `field` tokens. Any rename, spelling change, or mask/shift mismatch breaks compile-time expansion or silently targets the wrong hardware bits.

The visible register families in this chunk are:

- `BIFPLR3_0_PCIE_ESM_CAP_2` through `BIFPLR3_0_PCIE_ESM_CAP_7`: supported ESM data-rate bitmap fields for bridge/root-port instance 3. The chunk begins with the tail of `CAP_1` masks for `ESM_9P7G` through `ESM_10P9G`; nearby context shows `CAP_1` starts at `ESM_8P0G`.
- `BIFPLR4_0_*`: a full PCI/PCIe root-port/bridge configuration decode block for instance 4, including conventional PCI header fields, PCI PM capability, PCIe capability, MSI and subsystem IDs, vendor-specific and virtual-channel extended capabilities, AER, secondary PCIe, lane equalization, ACS, multicast, L1 PM substate, DPC, RP PIO error logging, and ESM capability fields.
- `BIFPLR5_0_*`: the start of the same configuration decode pattern for instance 5, covering vendor/device IDs, command/status, class/revision/header/BIST, bridge bus and window registers, capability pointer, interrupt line/pin, and bridge control.

## Important Register Groups

The BIFPLR3 and BIFPLR4 ESM groups expose a bitmap of link data rates. `PCIE_ESM_CAP_LIST`, `HEADER_1`, `HEADER_2`, `STATUS`, and `CTRL` describe an extended-speed-mode capability: vendor/capability metadata, minimum electrical-idle time, selected Gen3 and Gen4 ESM data rates, and the enable bit. `PCIE_ESM_CAP_1` through `CAP_7` then map individual 0.1 GT/s-style rate buckets from `ESM_8P0G` up to `ESM_28P0G`.

The conventional PCI bridge header fields for BIFPLR4 and BIFPLR5 include `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, class-code bytes, cache-line/latency/header/BIST bytes, bus-number routing, I/O and memory base/limit windows, prefetchable memory upper/lower windows, capability pointer, interrupt registers, and bridge controls. These fields mirror PCI bridge config-space layout and determine enumeration-visible capabilities and routing windows.

The BIFPLR4 PCI PM and PCIe capability fields include `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, slot/root registers, and the PCIe capability-2 registers. These masks cover power states, PME signaling, payload/read-request sizes, error-reporting enables, link speed/width, ASPM/clock-management controls, retraining, link status, slot hotplug signals, root PME/error reporting, completion timeout, ARI, AtomicOps, LTR, OBFF, and link-speed-vector information.

The BIFPLR4 MSI/SSID/MSI-map/VSEC/VC groups describe interrupt message routing, subsystem identity, fixed MSI mapping, vendor-specific extended capability scratch registers, and virtual-channel capability/resource controls for VC0 and VC1.

The BIFPLR4 reliability and isolation groups include AER uncorrectable/correctable error status, masks, severity, header and TLP-prefix logs, root-error command/status/source IDs, secondary PCIe lane equalization controls for lanes 0 through 15, ACS capability/control, multicast registers, L1 PM substate capability/control, DPC capability/control/status/source IDs, and RP PIO status/mask/severity/sys-error/exception/header-log/prefix-log fields.

## Control Flow

There is no runtime control flow in this chunk. The effective control flow happens in consumers:

1. A consumer includes `nbio_7_0_sh_mask.h` and the matching offset header.
2. It computes or names a register address, often via SOC15/NBIO register-address macros.
3. It reads a 16-bit or 32-bit register value from MMIO, PCIe indirect space, or config decode space.
4. It extracts a field with `(value & MASK) >> SHIFT` or `REG_GET_FIELD`.
5. For writes, it clears the mask and inserts a shifted field value with `REG_SET_FIELD` or a write-modify helper.

Because these are hardware-field constants, the relevant sequencing constraints are imposed by PCIe/NBIO hardware, not by this header. Fields such as `RETRAIN_LINK`, `SECONDARY_BUS_RESET`, DPC triggers, AER status bits, PME status, MSI enable, and ESM enable are especially order-sensitive when used by real driver code.

## State And Persistence Behavior

The header itself stores no state. The state represented by these masks is persistent hardware or PCI configuration state in the GPU/NBIO block:

- PCI bridge configuration fields can persist for the lifetime of device initialization and influence Linux PCI enumeration, BAR/window routing, bus mastering, memory access, SERR/parity reporting, and interrupt routing.
- PCIe capability and link-control fields affect link training, speed, width, equalization, ASPM, clock power management, and error reporting until changed by firmware, the kernel PCI core, or AMDGPU.
- AER, DPC, RP PIO, slot, root, and PME status fields may be latched by hardware and can require write-one-to-clear handling by consumers. The masks do not encode clear semantics, so call sites must know each register's access type.
- ESM capability/status/control fields describe and potentially select extended-speed-mode behavior. Incorrect writes can affect link reach, electrical-idle timing, or link negotiation.

## Dependencies And Integration Points

This file is guarded by `_nbio_7_0_SH_MASK_HEADER` and is included directly by `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Those consumers integrate NBIO masks into AMDGPU device bring-up, SOC15 register offset setup, and SMU/power-management code paths.

The field names are coupled to matching register-offset macros in headers such as `nbio_7_0_offset.h` and related NBIO version offset files. For example, BIFPLR ESM and config-decode registers have `regBIFPLR*_...` address macros and `..._BASE_IDX` values that select the correct SOC15 register base.

The helper dependency is mostly macro-level: `REG_GET_FIELD` and `REG_SET_FIELD` in `amdgpu.h` expect the `reg__field_MASK` and `reg__field__SHIFT` naming convention; SOC15 helpers in `soc15_common.h` provide register address calculation; `RREG32_PCIE*` and `WREG32_PCIE*` provide PCIe indirect access paths.

The hardware dependency is the NBIO 7.0 PCIe root-port/register specification. Several BIFPLR4 fields correspond to standardized PCI/PCIe capabilities, but the exact register packing and availability are ASIC-specific and generated here for this AMD block.

## Risks And Edge Cases

The main risk is silent bitfield drift. A wrong mask or shift can compile cleanly while causing the driver to read the wrong status bit or write adjacent control bits. For this chunk, high-impact examples include `COMMAND` access enables, `DEVICE_CNTL` payload/request sizes, `LINK_CNTL` retrain/link-disable bits, AER/DPC status and mask bits, bridge-window base/limit fields, and ESM enable/data-rate fields.

The chunk boundary starts mid-register at `BIFPLR3_0_PCIE_ESM_CAP_1` and ends mid-address-block at `BIFPLR5_0_IRQ_BRIDGE_CNTL`. Any generated-document merge must preserve that this research describes only this partial source range, not the complete file or complete BIFPLR5 block.

Reserved fields are explicitly exposed in some registers, while other registers omit unused bits. Consumers should avoid writing whole literal values based only on these masks unless they preserve unspecified/reserved bits through read-modify-write.

Several status/error registers likely include write-one-to-clear or sticky hardware behavior. This header does not distinguish read-only, read-write, write-one-to-clear, sticky, or strap-derived fields; users need the register spec or established call-site pattern before writing them.

The BIFPLR3/BIFPLR4/BIFPLR5 repetition is mechanical. Copy/paste or generation errors between instances could leave one root-port instance with a divergent field definition. Cross-checking against the generated offset header and sibling NBIO mask headers is useful when debugging instance-specific link behavior.

## Test Signals

There are no unit tests for this header alone. Useful validation signals are build-time and hardware/runtime oriented:

- Compile AMDGPU code that includes `nbio_7_0_sh_mask.h`; token-pasting users fail quickly if macro names are missing or malformed.
- Exercise AMDGPU probe/resume paths on NBIO 7.0 ASICs and verify PCIe link speed/width, bus-master and memory access, BAR/window enumeration, and interrupt routing remain correct.
- Compare decoded values from debugfs, MMIO traces, or PCI config dumps against expected PCI/PCIe fields, especially `LINK_STATUS`, `DEVICE_STATUS`, AER status, DPC status, and ESM status/control.
- Run suspend/resume, hot reset, link retraining, ASPM, AER/DPC injection, and PCIe error-recovery scenarios where these fields are most likely to be read or updated.
- For generated-header maintenance, diff this chunk against the hardware register database and sibling NBIO version headers to catch mask/shift drift before runtime testing.

### subset-b-003078: lines 24434-26840

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 24434-26840

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,176 `#define` field-layout macros and 229 register-family comments. It has no executable C statements, functions, structs, enums, variables, allocations, locks, or local storage.

The range starts with the final `BIFPLR5_0_IRQ_BRIDGE_CNTL__FAST_B2B_EN_MASK` macro from the previous register family, then covers the rest of the `BIFPLR5_0` PCIe bridge/root-port configuration-space field map from `EXT_BRIDGE_CNTL` through the PCIe Emergency Power Reduction/ESM capability registers. It then starts the `addressBlock: nbio_pcie0_bifplr6_cfgdecp` section and covers `BIFPLR6_0` PCI/PCIe bridge configuration fields from vendor/device ID through the shift definitions for `BIFPLR6_0_PCIE_UNCORR_ERR_STATUS`. The matching masks for that last `BIFPLR6_0_PCIE_UNCORR_ERR_STATUS` register begin after this chunk and belong to the next chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Purpose

`nbio_7_0_sh_mask.h` provides bit-level register-field constants for NBIO 7.0 hardware. For each field it exports the generated pair:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to place or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the encoded bit mask used to isolate, preserve, clear, or update that field.

This chunk describes PCI/PCIe bridge configuration-space fields for two NBIO PCIe logical root-port/bridge instances, primarily complete `BIFPLR5_0` coverage and partial `BIFPLR6_0` coverage. Driver code combines these constants with matching generated address/default headers and AMDGPU register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, and PCIe/SMN accessors. The constants let code name PCIe capability bits, error bits, link-control bits, and status bits instead of embedding raw bit positions.

## Important Macro Families

The `BIFPLR5_0` conventional PCI bridge and PCI Express capability portion includes:

- Power-management capability fields: capability-list IDs/next pointers, PME clock/init/current/support bits, power state, PME enable/status, B2/B3 support, bus power enable, and PMI data fields.
- PCIe capability, device, link, slot, and root fields: device type, slot implemented, interrupt message number, max payload/read request, relaxed ordering, extended tag, no-snoop, link speed/width, ASPM and clock power management controls, retrain/link-disable bits, slot power/hotplug controls, root error enables, and root PME status.
- PCIe capability version 2 fields: completion timeout support/value/disable, atomic operation routing/completer bits, LTR/OBFF/TPH related controls, IDO, emergency power reduction flags, 10-bit tag requester/completer support, link target speed, enter-compliance bits, equalization status, link bandwidth status, and lane margining style status bits.
- MSI and subsystem identity fields: MSI capability list, MSI enable/multiple-message/64-bit/per-vector masking controls, message address/data words, subsystem vendor/device IDs, MSI map capability and map address fields.
- Vendor-specific, virtual-channel, and device-serial-number enhanced capabilities: VSEC header/list fields, scratch registers, VC capability/control/status, VC0/VC1 resource capability/control/status, and serial number dwords.

The `BIFPLR5_0` PCIe error-reporting and recovery portions include:

- Advanced Error Reporting fields: uncorrectable error status/mask/severity bits for DLP, surprise down, poisoned TLP, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP-prefix blocked, and poisoned-TLP egress blocked conditions.
- Correctable error status/mask bits for receiver error, bad TLP, bad DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, header-log overflow, and virtual-channel non-fatal reporting.
- AER capability/control and root error command/status/source-ID fields, including first-error pointer, ECRC generation/check enable/capable bits, multiple header recording, TLP-prefix log presence, correctable/non-fatal/fatal error message enables, and received error message status bits.
- Header log and TLP prefix log registers, represented as full 32-bit log payload fields.
- Secondary PCIe capability, link control 3, lane error status, and per-lane 0 through 15 equalization controls for downstream/upstream transmit preset, coefficient, and preset-hint fields.

The access-control, multicast, low-power, and containment sections include:

- ACS capability/control bits for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, and egress vector size.
- Multicast capability/control/address/receive/block/overlay BAR fields, including multicast group counts, enable bits, egress blocking, overlay size, BAR index, and window base addresses.
- L1 PM substate capability/control fields for PCI-PM and ASPM L1.1/L1.2 support, common-mode restore times, T_POWER_ON scale/value, enable bits, LTR L1.2 threshold scale/value, and a separate T_POWER_ON value register.
- Downstream Port Containment capability/control/status/source-ID fields for trigger enables, completion control, interrupt enable/status, software trigger, poisoned-TLP egress blocking, RP busy, trigger reason, trigger reason extension, and first-error pointer.
- RP PIO status, mask, severity, system-error, exception, header log, implementation-specific log, and prefix-log registers for root-port PIO error reporting.
- ESM/Emergency Power Reduction fields: ESM capability list/header/status/control plus `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`, which enumerate supported ESM data rates from 8.0 GT/s-style entries through 28.0 GT/s-style entries at 0.1 increments.

The `BIFPLR6_0` portion repeats the same PCI/PCIe bridge configuration layout for another NBIO PCIe bridge instance, but only through the beginning of AER uncorrectable error status in this chunk. It includes vendor/device ID, command/status, class/revision/header/BIST, subordinate bus and bridge windows, interrupt and bridge-control fields, PM capability, PCIe capability, device/link/slot/root fields, version 2 capability fields, MSI/subsystem/MSI-map fields, VSEC/VC/serial-number fields, and the shift macros for AER uncorrectable error statuses.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor namespace for `BIFPLR5_0_*` and `BIFPLR6_0_*` register fields. The constants are untyped integer literals, mostly with an `L` suffix on masks, and encode only field geometry.

These macros do not define register addresses, access widths, reset values, write-one-to-clear behavior, side effects, polling rules, ownership, or sequencing. The companion `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, and `nbio_7_0_default.h` headers provide the related address and default-value metadata. Observed include users in this source tree include `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects the matching NBIO register address or PCIe configuration-space register from generated offset/SMN metadata.
2. The code reads the register through the SOC15, NBIO, PCIe, or SMN access path appropriate for the register.
3. It uses these `__SHIFT` and `_MASK` constants, often through `REG_GET_FIELD` or `REG_SET_FIELD`, to decode status or compose a modified value while preserving unrelated bits.
4. The resulting values guide PCIe bridge setup, link management, MSI programming, error reporting, DPC recovery, low-power substate configuration, virtual-channel setup, or hardware diagnostics.

The macro names imply several hardware-managed flows outside the header: PCIe link training and retraining, payload/read-request negotiation, hotplug/slot status propagation, MSI delivery, AER status latching and clearing, DPC triggering and recovery, RP PIO logging, L1 substate entry/exit, VC negotiation, multicast/ACS filtering, lane equalization, and ESM power-reduction capability selection.

## State And Persistence Behavior

The header owns no software state and persists nothing. It describes hardware-visible state in NBIO PCI/PCIe bridge configuration registers. Persistence depends on PCI reset, GPU reset domain, link reset, firmware/BIOS initialization, suspend/resume restore, power management, and explicit AMDGPU writes.

Represented state includes PCI command/status enables, bridge memory/I/O windows, power-management state and PME status, PCIe device/link/slot/root control and status, MSI address/data programming, subsystem identity, virtual-channel mappings, AER masks/severity/status/header logs, DPC state, PIO logs, L1 PM substate controls, ACS/multicast controls, lane equalization controls, and ESM capability/control state. Some fields are static capabilities, some are writable controls, some are live status bits, and some are sticky error/reporting latches. The macro definitions alone do not identify which category a field belongs to.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database staying synchronized across sibling headers:

- `nbio_7_0_offset.h` supplies register offsets such as `mm...` names for SOC15-style accesses.
- `nbio_7_0_smn.h` supplies SMN address definitions for NBIO/PCIe paths.
- `nbio_7_0_default.h` supplies reset/default values for matching `cfgBIFPLR5_0_*` and `cfgBIFPLR6_0_*` registers.
- AMDGPU register helper macros consume the `__SHIFT` and `_MASK` definitions to avoid hard-coded bit positions.

The broader integration points are AMDGPU NBIO and SOC15 initialization, power-management code that includes NBIO 7.0 metadata, PCIe link and bridge configuration, interrupt/MSI setup, AER/DPC/RAS style error handling, virtualization or topology paths that care about ACS/multicast/VC state, and hardware debug tooling that decodes PCIe logs or ESM capabilities. Cross-generation NBIO headers contain very similar names, but consumers must include the exact NBIO 7.0 address/mask/default set because field positions and register availability can differ by ASIC generation.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing software to read or write the wrong PCIe bridge bit. Symptoms may look like link-training failures, wrong payload sizing, MSI delivery failures, broken DPC/AER handling, or incorrect low-power behavior.
- This chunk has boundary incompleteness: it starts with one leftover `BIFPLR5_0_IRQ_BRIDGE_CNTL` mask whose shift is in the previous chunk, and it ends after the `BIFPLR6_0_PCIE_UNCORR_ERR_STATUS` shift macros but before their mask macros. Whole-file reconciliation must join adjacent chunks before treating those register families as complete.
- PCIe status, AER, DPC, and RP PIO fields may include sticky, write-one-to-clear, or hardware-updated bits. Blind read-modify-write using only masks can lose errors or clear state unexpectedly if the access semantics are not respected.
- Error mask and severity fields affect whether hardware reports, suppresses, or escalates PCIe failures. Incorrect defaults can hide link problems or create noisy fatal/non-fatal reporting.
- Link-control, link-control-2, equalization, and ESM fields are signal-integrity and link-stability sensitive. Bad writes may cause retraining loops, degraded link speed/width, or resume failures.
- Bridge window and bus-number fields describe PCI hierarchy routing. Misprogramming them can break config, memory, or I/O transactions below the bridge.
- ACS, multicast, VC, and MSI-map fields affect routing, isolation, and interrupt address behavior. Changes can have security or virtualization impact beyond a single driver call site.
- Capabilities and controls are mechanically repeated between `BIFPLR5_0` and `BIFPLR6_0`. Copying code across instances must still use the matching register address block and preserve instance-specific defaults.

## Test Signals

- Build AMDGPU/SOC15/NBIO 7.0 code paths with this header included; compile-time failures catch missing or renamed generated symbols used by consumers.
- Run generated-header consistency checks: every field should have a compatible `__SHIFT` and `_MASK`, masks within a register should not overlap unexpectedly, and repeated `BIFPLR5_0`/`BIFPLR6_0` layouts should match where the hardware database says they are identical.
- Cross-check this chunk against `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, and `nbio_7_0_default.h` so each named register maps to an address and expected default value.
- On supported NBIO 7.0 hardware, validate PCIe enumeration, bridge window setup, MSI operation, link speed/width negotiation, link retraining, suspend/resume, GPU reset recovery, and low-power L1 substate behavior.
- Exercise PCIe error paths where hardware or platform validation allows it: AER correctable/uncorrectable reporting, DPC trigger/recovery, root error status/source-ID decoding, header/TLP-prefix logs, and RP PIO logs.
- For code that writes any field from this chunk, inspect register traces to ensure reserved and unrelated bits are preserved and sticky status bits are handled with the documented clear semantics.

### subset-b-003079: lines 26841-29278

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 26841-29278

## Scope And Purpose

This chunk is a generated NBIO 7.0 register field-mask slice. It contains no executable code; its public surface is a large set of C preprocessor constants that describe bit positions and already-shifted bit masks for hardware registers. Consumers pair these definitions with the matching NBIO 7.0 register-address header and AMDGPU MMIO/SMN register access helpers to encode writes, decode reads, and preserve fields during read-modify-write sequences.

The range starts in the tail of `BIFPLR6_0_PCIE_UNCORR_ERR_STATUS`, then covers PCIe advanced error reporting, link/lane capability, access control services, multicast, L1 PM substates, downstream port containment, root-port PIO logging, and Equalization Status Method fields. It then moves through DBGU indexed debug ports, GDC doorbell and miscellaneous controls, SYSHUB clock/power/QoS controls, NIC400 fabric issue-override fields, SION arbitration/credit controls, SHUB reset controls, GDC RAS leaf controls, and the first IOMMU L2 MMIO base-address registers.

This chunk contains 2,135 `#define` entries: 1,061 `__SHIFT` macros and 1,074 `_MASK` macros. The small mismatch is expected at chunk boundaries and because the first visible lines continue masks for a register whose shift definitions appear before this chunk.

## Register Families Covered

The PCIe block covers multiple capability and error-management areas for `BIFPLR6_0`. AER-related definitions include uncorrectable error mask and severity bits for data-link, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable, multicast-blocked, atomic-op egress-blocked, TLP-prefix-blocked, and poisoned-TLP egress-blocked errors. Correctable error status/mask fields cover receiver error, bad TLP/DLLP, replay rollover/timeout, advisory nonfatal, internal correctable, and header-log overflow bits. Header, prefix, source-ID, root-error-command, and root-error-status registers provide error reporting and diagnostic log metadata.

The PCIe extended capability definitions include secondary enhanced capability, link control 3, lane error status, per-lane equalization controls for lanes 0 through 15, ACS capability/control, multicast capability/control/address/receive/block/overlay BAR fields, L1 PM substate capability/control/timing fields, DPC capability/control/status/source-ID fields, and root-port PIO status/mask/severity/system-error/exception plus header/prefix log windows. The ESM area describes capability headers, minimum electrical-idle timing, Gen3/Gen4 data-rate controls, an enable bit, and dense capability bitmaps for rates from 8.0G through the high 20G ranges across `ESM_CAP_1` through `ESM_CAP_7`.

The `nbio_dbgu0_dbgudec` address block defines four indexed debug ports. Each port has an address register with `Index`, reserved bits, and `ReadEnable`, plus low/high 32-bit data windows. These are low-level debug access windows rather than normal driver state variables.

The `nbio_nbif0_gdc_GDCDEC` block describes GDC/NGDC and doorbell-related fields. It includes SDP disconnect hysteresis, dropping non-PF MMREG requests, reserved 32-bit windows, SDMA0/SDMA1/IH/MMSCH doorbell range offset and size fields, ATDMA weighted round-robin controls, a doorbell fence enable, 64-bit doorbell support disable bits for SDMA and CP, AXI host completion endpoint disable, and a GDC power-gating reset-select bit.

The `nbio_nbif0_syshub_mmreg_direct_syshubdirect` block is the largest non-PCIe block in this chunk. It defines SOCCLK and SHUBCLK deep-sleep controls for HST and DMA client lanes, deep-sleep timers, BGEN bypass/immediate enable bits, DMA QoS max/min/mode fields, per-clock/per-client control registers with FLR-on-reset, link-reset-on-reset, static QoS override, read WRR weight, and write WRR weight fields. It also exposes SYSHUB clock-gating control, per-VF/PF transaction-idle status bits, high-precision timer and scratch windows, MGCG controls, CL masking for MP1/MP1DRAM, and NIC400 `read_iss_override` / `write_iss_override` fields for several ASIB/AMIB interfaces.

The `nbio_nbif0_nbif_sion_SIONDEC` block is dominated by repeated SION class-of-service controls. For CL0 through CL3, it defines read-response, write-response, and request burst-target/time-slot registers and request/data/read-response/write-response pool credit allocations. Each of these simple windows exposes a full-width `DATA` field. `SION_CNTL_REG0` adds many clock soft-override bits, while `SION_CNTL_REG1` defines livelock watchdog threshold and clock-gating-off hysteresis fields.

The `nbio_nbif0_gdc_rst_GDCRST_DEC` block covers reset controls. It includes PF FLR reset bits for device 0 and device 1 PF0 through PF7, a graphics driver VPU reset bit, link P0/P1 reset bits, PF0 VF0 through VF15 FLR reset bits plus a PF0 soft-PF FLR reset bit, hard and soft reset enable bits for COR/REG/STY/NIC400/SDP port reset domains, an SDP port reset bit, and RSMU soft-reset atomic/cycle fields.

The `nbio_nbif0_gdc_ras_gdc_ras_regblk` block defines six identical-looking RAS leaf controls. Each leaf has poison and parity detection enable, error-event enable, stall enable, local error reporting enable, event/link-disconnect receive status, poison/parity detected status, error-event sent, and egress-stalled bits.

The chunk ends at the beginning of `nbio_iohub_iommu_l2mmio_l2mmiocfg`. Visible IOMMU L2 MMIO registers define low/high portions and length fields for the device table base, command buffer base, and event log base, with reserved masks included in the layout. The final `IOMMU_L2MMIO0_IOMMU_MMIO_EVENT_BASE_1` register is cut off by the chunk boundary; its remaining masks continue in a later chunk.

## APIs, Types, And Functions

There are no functions, structs, enums, inline helpers, or runtime APIs in this chunk. The important interface is the generated naming convention:

- `<REGISTER>__<FIELD>__SHIFT` is the zero-based bit position of a field.
- `<REGISTER>__<FIELD>_MASK` is the field mask in register position.
- Full-width data/log registers use masks such as `0xFFFFFFFFL`; shorter PCIe capability registers often use 16-bit masks, while NBIF/SYSHUB/GDC/SION blocks generally use 32-bit masks.

Normal consumers are AMDGPU register manipulation paths that read a register, clear the field mask, OR in `(value << SHIFT) & MASK`, then write it back. Diagnostic paths use the same pairs to decode status, error, credit, QoS, reset, RAS, and IOMMU base-address fields.

## Control Flow

The header has no runtime control flow. All behavior is deferred to whichever driver, firmware interface, debug tool, or generated access helper includes these macros.

The field names imply several sequencing-sensitive hardware protocols. PCIe AER, DPC, root-port PIO, and ESM fields require capability discovery, status collection, mask/severity programming, and bounded recovery or logging sequences. SYSHUB, SION, and GDC fields influence clock gating, QoS, arbitration credits, doorbell routing, and fabric resets, so writes must follow the hardware's ordering rules. Reset and FLR fields are especially stateful: asserting PF/VF, link, hard, or soft resets without waiting for completion or preserving unrelated bits can interrupt live functions. IOMMU base registers must be programmed coherently across low/high halves and length fields before enabling translation or command/event handling.

## State And Persistence Behavior

The file stores no software state and performs no persistence. It describes hardware state that persists in NBIO registers until reset, power transition, firmware action, or driver write.

State categories visible in this chunk include PCIe error status, masks, severities, root error source IDs, header and prefix logs, lane equalization settings, ACS and multicast controls, L1 substate controls, DPC trigger/status state, ESM rate capabilities/enables, DBGU indexed debug data, GDC doorbell ranges and fences, SYSHUB deep-sleep/clock-gating/QoS/idle state, NIC400 issue-override bits, SION arbitration and credit allocation state, SHUB reset request state, RAS detection/reporting/stall state, and IOMMU device-table/command/event base-address state.

Reserved fields are explicitly defined in several registers. They are part of the documented bit layout, but driver writes should not treat them as feature state. Read-modify-write paths should preserve reserved bits unless the hardware specification requires a fixed write value.

## Dependencies And Integration Points

This chunk depends on the rest of the generated NBIO 7.0 register package. The matching offset header supplies addresses for the registers named here, the default header supplies reset/default values where generated, and adjacent chunks of `nbio_7_0_sh_mask.h` define the preceding and following fields cut by this line range.

Integration is hardware-facing and primarily through AMDGPU NBIO, PCIe, SR-IOV, reset, RAS, IOMMU, doorbell, clock/power-management, and low-level diagnostic code. The BIFPLR6 PCIe fields align with PCIe capability and error-handling flows. GDC and SHUB reset fields align with FLR, link reset, and NBIF reset handling. Doorbell ranges and fence controls affect SDMA, IH, CP, and MMSCH doorbell routing. SYSHUB/SION fields affect fabric QoS, clock gating, transaction-idle checks, and credit arbitration. IOMMU L2 MMIO base fields are integration points for GPU-side IOMMU table, command, and event-log setup.

## Risks And Edge Cases

Generated shift/mask headers are passive data, but mistakes are high-impact because consumers write directly to hardware. A wrong mask or shift can alter PCIe error policy, disable doorbell support, change QoS arbitration, reset the wrong PF/VF, corrupt RAS reporting, or program an invalid IOMMU base.

Many fields represent write-one, sticky status, or clear-on-write hardware state in the underlying registers, but this header does not encode access semantics. Callers must know whether a field is read-only, write-one-to-clear, sticky, reset-sensitive, or preserved across power states.

The PCIe section mixes 16-bit capability-style registers, 32-bit status/log registers, and dense per-lane/per-rate arrays. Generic code should not infer register width solely from the namespace. The chunk boundary also begins and ends mid-register-family: uncorrectable error status starts before line 26841, and `IOMMU_MMIO_EVENT_BASE_1` continues after line 29278.

Reset and FLR fields are risky in virtualized environments. `SHUB_PF_FLR_RST` and `SHUB_PF0_VF_FLR_RST` expose per-function reset controls; writing the wrong bit can disrupt another PF/VF or leave functions stuck if polling and deassert sequencing are wrong.

IOMMU base fields split addresses across low/high registers with reserved bits and length fields. Code must enforce alignment, program both halves consistently, avoid tearing while the unit is active, and preserve reserved bits.

QoS, SION credits, SYSHUB clock gating, MGCG, and deep-sleep controls can cause performance regressions or hangs if programmed without workload and power-state awareness. RAS poison/parity stall settings can intentionally stop egress traffic; enabling stall paths without recovery handling can wedge the affected leaf.

## Test Signals

Primary validation for this header is successful compilation of AMDGPU code that includes the generated NBIO 7.0 register package. Because this chunk has no executable logic, behavioral confidence comes from static generated-header checks plus hardware, simulator, or register-trace validation.

Useful static checks include verifying that each field normally has both a shift and mask, that masks align with shifts and widths, that duplicate lane/rate/client arrays are monotonic, that reserved masks do not overlap active fields within a register, and that chunk-boundary exceptions are accounted for during merge.

Useful runtime or integration signals include PCIe AER/DPC/root-port PIO tests that inject correctable and uncorrectable errors and validate status, mask, severity, source-ID, header-log, prefix-log, and DPC status decoding; link training and compliance traces that validate lane equalization and ESM rate fields; SR-IOV reset tests that exercise PF/VF FLR and link reset bits with bounded polling; doorbell tests that verify SDMA/IH/CP/MMSCH routing and 64-bit support flags; clock/power tests that observe SYSHUB transaction-idle, deep-sleep, MGCG, and scratch/timer behavior; QoS and SION stress tests that check arbitration credit programming and livelock watchdog behavior; RAS tests that inject poison/parity events and observe leaf event, stall, and reporting bits; and IOMMU setup tests that validate device table, command buffer, and event log base programming against real translated traffic and event generation.

Merged per-file research should connect this chunk with adjacent `nbio_7_0_sh_mask.h` chunks for the complete generated field map and with the matching NBIO 7.0 offset/default headers for addresses, reset values, and access widths.

### subset-b-003080: lines 29279-31718

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 29279-31718

## Scope And Purpose

This chunk is a generated AMD NBIO 7.0 register field header segment. It defines `__SHIFT` and `__MASK` constants for fields in several NBIO address blocks: IOMMU L2 MMIO control/status, IOMMU queue and counter state, IOAPIC MMIO/index registers, and the start of the NBIF0 BIF root-complex PCI configuration space for device 0 RC1.

The header contains no executable functions or types. Its purpose is to make register programming in the AMDGPU driver readable and mechanically consistent: call sites include the paired offset header for register addresses and this shift/mask header for field extraction or read/modify/write composition. Consumers use these constants with AMDGPU register helpers, `REG_GET_FIELD`-style macros, and direct bit operations when configuring NBIO, PCIe, IOMMU, interrupt, and power-management behavior.

This chunk starts just after the IOMMU event-base fields and opens with `IOMMU_L2MMIO0_IOMMU_MMIO_CNTRL_0`. It ends at the declaration of `BIF_CFG_DEV0_RC1_SLOT_STATUS`, before that register's field definitions continue in the next chunk.

## Register Areas Covered

The first major area is `nbio_iohub_iommu_l2mmio_l2mmiocfg`. It covers AMD IOMMU MMIO controls such as `IOMMU_EN`, command/event logging enable bits, event/PPR/GA interrupt enables, coherent/isoc behavior, guest translation and address translation support, SMIF/GAM toggles, and queue sizing fields. Capability registers `EFR_0` and `EFR_1` expose feature support for prefetch, PPR, guest translation, x2APIC/NX-like support bits, HATS/GATS/GLX, SMIF, GAM, PASID maximum, DTE segmenting, automatic PPR response, MARC, MSI capability, snoop attributes, HA/EPH/ATTRFW/HD, and IOTLB invalidation type support.

The same IOMMU block defines address and size fields for exclusion ranges, PPR queues, GA log buffers, duplicated B-side PPR/event queues, and alternate device-table bases `DEVTBL_1` through `DEVTBL_7`. Base and limit values are split into low/high halves, with low-address fields commonly shifted by 12 and high halves carrying 20-bit masks, reflecting page-aligned physical address programming.

Queue pointer and status definitions cover command, event, PPR, GA, PPR_B, and EVENT_B buffers. Each queue has head and tail pointer fields, usually aligned on low reserved bits and paired with reserved high bits. `IOMMU_MMIO_STATUS_0` reports queue activity, log interrupts, command-buffer running state, event/PPR/GA overflow, B-side overflow, buffer-active state, and early-overflow conditions.

The performance-counter section describes IOMMU counter topology and two banks with four counters each. Each counter group includes a 48-bit counter split into low/high registers, an event source selector (`CSOURCE`), count units, clear/active control (`CAC`), PASID/domain/device-ID match fields and masks with enable bits, and event-note report fields with a report-enable bit (`CERE`). Bank lock registers separately cover PASID, domain, and device-ID lock masks.

The next address blocks are IOAPIC-related. `nbio_iohub_nb_ioapicmio_ioapic_miodec` defines the IOAPIC index/data windows, an IRQ pin assertion register, and an EOI vector register. `nbio_iohub_nb_ioapicmioindex_ioapic_mioindexdec` defines indexed IOAPIC ID/version/arbitration fields and redirection table entries 0 through 31. Each redirection entry low half has vector, delivery mode, destination mode, delivery status, polarity, remote IRR, trigger mode, and mask fields; each high half has the destination APIC ID.

The final area in this chunk begins `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` and covers PCI/PCIe root-complex config-space fields for `BIF_CFG_DEV0_RC1`. It includes vendor/device ID, command/status, revision/class/header/BIST fields, bridge bus numbering, IO/memory/prefetchable windows, interrupt and bridge control fields, PCI power-management capability fields, and PCIe capability fields. The visible PCIe capability portion covers device capability/control/status, link capability/control/status, and slot capability/control before stopping at `SLOT_STATUS`.

## Important Definitions

The most important API surface is the naming contract:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit index used before masking or after extraction.
- `<REGISTER>__<FIELD>_MASK` gives the already-positioned field mask, usually suffixed with `L`.
- Comment lines such as `//IOMMU_L2MMIO0_IOMMU_MMIO_CNTRL_0` and `// addressBlock: ...` segment fields by hardware register and address block.

High-impact field groups include:

- IOMMU control: `IOMMU_EN`, `CMD_BUF_EN`, `EVENT_LOG_EN`, `EVENT_INT_EN`, `PPR_LOG_EN`, `PPR_INT_EN`, `PPR_EN`, `GT_EN`, `GA_EN`, `SMIF_EN`, `GAM_EN`, `GA_LOG_EN`, `GA_INT_EN`, and `PPRQ`.
- IOMMU capabilities: `PREF_SUP`, `PPR_SUP`, `GT_SUP`, `GA_SUP`, `HATS`, `GATS`, `GLX_SUP`, `SMIF_SUP`, `GAM_SUP`, `PAS_MAX`, `DTE_seg`, `PPR_AUTORESP_SUP`, `MARCnum`, `MMIO_MSI_CAP_SUP`, and `InvIotlbTypeSup`.
- Queue state: `CMD_HDPTR`, `CMD_TAILPTR`, `EVENT_HDPTR`, `EVENT_TAILPTR`, `PPR_HDPTR`, `PPR_TAILPTR`, `GA_HDPTR`, `GA_TAILPTR`, and B-side equivalents.
- IOMMU status: `EVENT_OVERFLOW`, `EVENT_LOGINT`, `COMWAIT_INT`, `CMD_BUFRUN`, `PPR_OVERFLOW`, `PPR_INT`, `GA_OVERFLOW`, `GA_INT`, `EVENT_B_OVERFLOW`, and early-overflow flags.
- IOMMU counters: `N_COUNTER`, `N_COUNTER_BANKS`, `ICOUNTER_*`, `CSOURCE_*`, `COUNT_UNITS_*`, `CAC_*`, `PASID_MATCH/MASK`, `DOMAIN_MATCH/MASK`, `DEVICEID_MATCH/MASK`, and report `EVENT_NOTE`/`CERE` fields.
- IOAPIC redirection: `Vector_N`, `Delivery_Mode_N`, `Destination_Mode_N`, `Interrupt_Pin_Polarity_N`, `Remote_IRR_N`, `Trigger_Mode_N`, `Mask_N`, and `Destination_id_N`.
- Root-complex config: bridge command/status bits, bus number/window fields, PM capability/status bits, PCIe link speed/width, link retrain/disable/control bits, error enable/status bits, FLR capability, and slot hotplug/power/indicator controls.

## Control Flow And Data Flow

There is no local control flow in this header. Runtime flow is indirect: AMDGPU initialization, interrupt setup, PCIe link handling, power-management code, and low-level NBIO helpers include this file and use the constants to read a register, isolate fields, compose new values, and write them back.

The effective flow at call sites is normally:

1. Select a register address from a matching `nbio_7_0_offset.h` or related offset header.
2. Read the register through MMIO, PCI config, or indexed IOAPIC access helpers.
3. Extract a field with the mask and shift, or clear and insert a new field value.
4. Write the modified value back, preserving reserved bits where the hardware requires it.

Because this file defines only bit positions, correctness depends on consumers pairing these masks with the matching NBIO generation and register address block. A correct mask applied to the wrong register can silently program a different hardware field.

## State And Persistence Behavior

The header itself has no state, allocation, locking, or persistence. The hardware registers it describes are persistent hardware state across driver operations until reset, power transition, firmware action, or later driver writes alter them.

The IOMMU definitions affect durable device state such as command/event/PPR/GA queue base addresses, head/tail pointers, interrupt enables, exclusion ranges, MARC remap windows, and performance-counter configuration. Incorrect values can persist long enough to break DMA translation, event delivery, or queue processing until the device or function is reset.

The IOAPIC redirection fields define interrupt routing state. Vector, delivery mode, polarity, trigger mode, mask, and destination changes directly control how NBIO-originated interrupts are delivered to the host.

The BIF RC1 PCI config fields describe bridge-visible state exposed to the PCI subsystem. Command bits, memory/IO windows, PM state, PCIe link controls, and slot/hotplug controls can affect enumeration, link training, error reporting, power management, and device reset behavior.

## Dependencies And Integration Points

This chunk is included through AMDGPU NBIO and SoC support code, notably files such as `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and SMU10 power-management includes. It must remain synchronized with the matching offset headers and generated register database for NBIO 7.0.

Important integration points include:

- AMDGPU register access helpers that expect these masks to be already shifted into register position.
- PCIe/NBIO code that interprets root-complex config registers and link status fields.
- IOMMU programming and diagnostics paths that manage device tables, queue buffers, PASID/domain/device matching, and event logs.
- Interrupt routing code that accesses IOAPIC indexed registers and redirection entries.
- Firmware and hardware documentation contracts: many fields are reserved, capability-only, or split across low/high registers, so preserving reserved bits and programming paired registers in the right order is part of the external contract.

## Risks And Edge Cases

The main risk is generated-data drift. If a shift or mask is wrong, driver code will still compile, but it may read false capability data, write reserved bits, corrupt queue pointers, disable interrupts, misroute IOAPIC entries, or report incorrect PCIe link state.

Split address fields are especially sensitive. Many base/limit registers expose low fields starting at bit 12 and high fields masked to 20 bits. Call sites must maintain page alignment, combine low/high halves correctly, and avoid truncating physical addresses.

Queue pointer fields reserve low alignment bits and high unused bits. Bugs here can make command/event/PPR/GA queues appear empty, full, or active forever. Overflow and early-overflow masks are also status-like fields, so consumers must know whether hardware uses write-one-to-clear or read-only semantics from the register spec; the header does not encode that behavior.

Reserved masks are present throughout the chunk. They are useful for decoding but risky for writes: code should not use `Reserved*_MASK` as writable fields unless the hardware programming guide explicitly requires it.

IOAPIC redirection entries are repetitive and index-sensitive. A copy/paste or generation error for one entry can affect only a specific interrupt line, making failures intermittent and platform-dependent.

The BIF RC1 config fields mix standard PCI/PCIe semantics with AMD-specific root-complex placement. Link retraining, link disable, clock power management, hotplug interrupt enables, bridge window, and SERR/error bits can have visible system behavior. Misprogramming can affect boot enumeration, suspend/resume, GPU reset, AER-like reporting, or hotplug handling.

## Test Signals

There are no unit tests for this header alone. Useful signals come from build coverage and hardware/integration behavior:

- Compile tests for AMDGPU configurations that include NBIO 7.0 ensure symbol names and include ordering remain valid.
- PCI enumeration and `lspci`/kernel logs can reveal broken vendor/device ID, class, bridge window, command/status, or PCIe capability decoding.
- GPU initialization, reset, suspend/resume, and runtime power-management tests exercise NBIO register programming paths using these masks.
- IOMMU and DMA stress tests can expose bad device-table, queue, PASID/domain/device-ID, event-log, or PPR/GA fields through translation faults, hangs, or missing interrupts.
- Interrupt-routing tests and normal display/compute interrupt traffic can expose IOAPIC redirection mistakes through lost, masked, or misdelivered interrupts.
- PCIe link training and error-injection diagnostics can validate `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, device status, root control, and slot-control fields.

For review, the strongest static check is diffing this generated chunk against the authoritative AMD register database or an adjacent known-good NBIO generation, while verifying that all consumers include the matching offset header for the same ASIC generation.

### subset-b-003081: lines 31719-34187

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 31719-34187

## Scope

This chunk covers a generated AMD NBIO 7.0 shift/mask header segment for PCIe/NBIO register fields. It contains only preprocessor constants: one `__SHIFT` macro and one `_MASK` macro for each named bitfield. There are no C functions, structs, enums, variables, branches, locks, allocations, persistence objects, or direct hardware accesses in this range.

The chunk starts inside `BIF_CFG_DEV0_RC1_SLOT_STATUS`; its register comment and any fields before `ATTN_BUTTON_PRESSED` are in the previous chunk. It ends inside `BIF_BX_PF0_MM_CFGREGS_CNTL` after `MM_WR_TO_CFG_EN__SHIFT`; the mask definitions for that final register continue in the next chunk.

The visible address-block coverage is:

- Tail of `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`: `BIF_CFG_DEV0_RC1_*` root-complex PCI configuration, MSI, vendor-specific capability, virtual channel, AER, link equalization, and ACS fields.
- Full visible `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp`: `BIF_CFG_DEV1_RC1_*` PCI/PCIe root-complex configuration fields from IDs and command/status through ACS.
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC`: indirect MMIO index/data aperture fields for PF0.
- `nbio_nbif0_bif_bx_pf_SYSDEC`: syshub/PCIe indirect apertures, SBIOS/BIOS scratch fields, RLC/VCE/UVD interrupt controls, and GFX MMIO CAM remap/control fields.
- `nbio_nbif0_rcc_strap_BIFDEC1`: device/function strap fields for RCC device 0 endpoint function 0.
- `nbio_nbif0_rcc_ep_dev0_BIFDEC1`: endpoint-side PCIe control, interrupt, LTR, DPA, PME, TX, error, RX, and link-speed fields.
- `nbio_nbif0_rcc_dwn_dev0_BIFDEC1` and `nbio_nbif0_rcc_dwnp_dev0_BIFDEC1`: downstream PCIe control, error, RX, link-speed, strap, and LTR-message fields.
- Start of `nbio_nbif0_bif_bx_pf_BIFDEC1`: BIF PF0 indirect-access disable, bus control, scratch, reset-enable, and start of MM config-register control fields.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.0 register interface. The matching register addresses live in `nbio_7_0_offset.h`, while reset/default values live in adjacent generated default headers. Runtime driver code includes this file so it can compose, extract, and update hardware register fields through the common AMDGPU register-helper convention rather than open-coding bit positions.

This chunk is centered on PCIe root-complex and NBIF bridge configuration surfaces. The `BIF_CFG_DEV0_RC1_*` and `BIF_CFG_DEV1_RC1_*` families expose PCI-compatible configuration fields such as command/status, bridge bus-number windows, I/O and memory base/limit registers, interrupt and bridge control, power-management capability, PCIe device/link/slot/root controls, MSI/MSI-map capability, virtual-channel capability and resources, AER status/mask/severity/header logs, secondary PCIe capability, per-lane equalization controls, and ACS capability/control. The later BIF/RCC blocks expose indirect register apertures, scratch registers, firmware-visible BIOS scratch space, block interrupt controls, MMIO CAM remapping, strap-derived device identity, endpoint/downstream PCIe behavior overrides, LTR/DPA controls, and error-reporting knobs.

This repository path is under a Ceph/distributed-filesystem mirror, but this header segment belongs to the mirrored Linux AMDGPU driver tree and has no Ceph filesystem behavior.

## Important APIs, Types, and Functions

There are no callable APIs, C types, or functions in this chunk. The public interface is the macro namespace. Each macro follows one of the generated forms:

- `<REGISTER>__<FIELD>__SHIFT` gives the zero-based bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask with the field already shifted into register position.

The register-helper contract is important. AMDGPU code can use these definitions with helpers such as `REG_GET_FIELD()` and `REG_SET_FIELD()` when the register offset macro has the same `<REGISTER>` stem. For example, command/status and PCIe-control fields can be read, masked, shifted, and updated without spelling raw bit numbers. Multi-bit masks in this range include bus numbers, bridge windows, payload/request sizes, link widths/speeds, completion timeout values, VC/TC mapping, AER header-log controls, equalization presets, DPA power allocation values, LTR timing values, and traffic-class selections.

Important field groups visible in this chunk include:

- PCI command/status and bridge windows: `IOEN_DN`, `MEMEN_DN`, `BUS_MASTER_EN`, parity/SERR/int-disable bits, primary/secondary/subordinate bus numbers, I/O and memory base/limit fields, prefetchable-window upper registers, and bridge control.
- PCIe capability fields: device capabilities and controls for payload, relaxed ordering, phantom functions, extended tag, No Snoop, AUX power, errors, FLR, link speed/width, ASPM, read completion boundary, link retrain, common clock, slot power/hotplug, root error/PME controls, and CRS visibility.
- MSI and subsystem fields: MSI enable/multiple-message/64-bit/per-vector mask capability, MSI message address/data fields, subsystem vendor/device IDs, and MSI-map control/address fields.
- PCIe extended capabilities: vendor-specific capability headers/scratch, VC port and resource controls, device serial number, AER uncorrectable/correctable status/mask/severity, AER capability/control, header/TLP prefix logs, root error command/status/source IDs, secondary PCIe link/equalization, per-lane equalization controls for lanes 0-15, and ACS capability/control fields.
- Indirect apertures and scratch: `BIF_BX_PF0_MM_INDEX`, `MM_DATA`, `MM_INDEX_HI`, `SYSHUB_INDEX_OVLP`, `SYSHUB_DATA_OVLP`, `PCIE_INDEX`, `PCIE_DATA`, `PCIE_INDEX2`, `PCIE_DATA2`, `SBIOS_SCRATCH_0..3`, and `BIOS_SCRATCH_0..15`.
- BIF/RCC controls: block interrupt controls for RLC/VCE/UVD, GFX MMIO CAM address/remap/enable/completion fields, RCC endpoint/downstream error reporting, hidden-register decode enables, LTR controls, DPA power allocation, PME control, PCIe TX requester ID, RX ignore controls, link-speed straps, downstream FLR/timeout controls, and PF0 bus/reset/MM-config fields.

## Control Flow

This header has no local control flow. It participates in external driver control flow as a constants provider:

1. Generation-specific AMDGPU code selects an NBIO 7.0 register offset from the matching offset header.
2. The code reads a PCIe/NBIO register through MMIO, SMN, PCI config-space, or an indirect index/data aperture.
3. The code uses this header's `__SHIFT` and `_MASK` constants to extract fields or compose a read-modify-write value.
4. The hardware, firmware, PCIe core, or NBIO block observes the resulting register value and performs the actual side effect.

The chunk's fields therefore support flows such as PCIe root-port discovery, bridge-window setup, error reporting/AER handling, link training and equalization, MSI setup, ACS isolation, virtual-channel configuration, firmware handoff through scratch registers, MMIO indirect access, block-level interrupt routing, GPU reset/FLR behavior, LTR/DPA power management, and endpoint/downstream error policy. The header itself does not enforce ordering, polling, locking, or reset sequencing.

## State and Persistence Behavior

No software state is stored here. All state described by the macros lives in NBIO, PCIe, BIF, RCC, firmware scratch, or strap-backed hardware registers once external code reads or writes the corresponding offsets.

State behavior varies by register family:

- PCI configuration and PCIe capability/control fields are hardware-visible configuration state. Some bits are set by enumeration or driver initialization, some are status bits, and others can be write-1-to-clear or write-sensitive depending on the PCIe/AER specification and the ASIC register database.
- AER status, root error status, header logs, TLP prefix logs, lane error status, interrupt status, and DPA/PME status-like fields are hardware-observed diagnostic or event state. They may be cleared by writes, reset by function reset, or updated asynchronously by PCIe hardware.
- `SBIOS_SCRATCH_*` and `BIOS_SCRATCH_*` are scratch registers intended for firmware/BIOS/driver coordination. Their persistence depends on ASIC reset domains and boot firmware policy; treating them as driver-private storage is unsafe without ownership knowledge.
- Strap fields such as `STRAP_DEVICE_ID_DEV0_F0`, revision IDs, function enable, legacy device type, and D-state support reflect boot-time strap/fuse/configuration values and should generally be considered hardware-initialized identity/capability state.
- Indirect aperture registers (`MM_INDEX`, `MM_DATA`, `PCIE_INDEX`, `PCIE_DATA`, syshub index/data) hold addressing and data windows for other register spaces. Their values may be transient cursor state for an access sequence and can race if shared without the driver's existing serialization.
- Reset and FLR-related bits (`BX_RESET_EN`, downstream `FLR_EXTEND_MODE`, reset-on-VF-enable-low, FLR twice enable) influence recovery behavior rather than storing durable user data.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.0 register header set:

- `nbio_7_0_offset.h` supplies the matching register offsets for the same register stems.
- `nbio_7_0_default.h` or related generated default headers supply reset values where available.
- AMDGPU's common register helper macros consume the `__SHIFT` and `_MASK` naming convention.

Integration points in the wider AMDGPU tree include NBIO generation code, PCIe configuration and link-management code, interrupt setup, GPU reset/FLR paths, SR-IOV/VF/PF handling, power-management code that relies on LTR/DPA/ASPM-related fields, error reporting/AER diagnostics, and firmware/BIOS handoff logic that reads scratch or strap fields. The `BIF_BX_PF0_*` indirect aperture and MMIO CAM fields also integrate with lower-level register access paths because they can redirect or expose otherwise hidden register windows.

The fields align with standard PCI/PCIe concepts, but the actual register addresses and some names are ASIC-specific. Code must pair these masks with NBIO 7.0 offsets, not with similar-looking masks from other NBIO generations or device instances.

## Risks and Edge Cases

- The chunk starts and ends mid-register. `BIF_CFG_DEV0_RC1_SLOT_STATUS` is incomplete at the start, and `BIF_BX_PF0_MM_CFGREGS_CNTL` is incomplete at the end. Final per-file research must merge neighboring chunks before claiming complete coverage of those registers.
- Many fields mirror PCIe specification bits with precise write semantics. Misusing status masks as normal read-write bits can lose AER/error evidence or accidentally clear interrupt/status conditions.
- DEV0 and DEV1 root-complex families are structurally similar. Copying a `BIF_CFG_DEV0_RC1_*` mask to a `BIF_CFG_DEV1_RC1_*` register, or the reverse, may compile if the field shape matches but operate on the wrong device instance.
- Per-lane equalization controls are repeated for lanes 0-15. Off-by-one lane selection or a missing lane in generated data can produce subtle link-training failures that are not caught by simple compile tests.
- ACS, peer-to-peer redirect, translation blocking, and upstream-forwarding bits affect DMA isolation and topology behavior. Incorrect masks can weaken isolation or break peer-to-peer traffic.
- AER mask/severity/status fields determine whether errors are surfaced, suppressed, or classified fatal/nonfatal. Generation drift in these constants can hide hardware faults or create spurious fatal handling.
- Indirect index/data aperture fields are shared access mechanisms. A driver sequence that updates index and data without appropriate locking or ordering can read/write an unintended target register.
- BIOS/SBIOS scratch registers are integration points with firmware. Driver changes that overwrite undocumented scratch content can break boot handoff, resume, reset recovery, or board-specific workarounds.
- Strap-derived fields are often read-only or boot-latched. Treating them as writable configuration can be ineffective or harmful depending on the actual hardware access policy.
- Several fields use high bits, full 32-bit masks, or 64-bit-related address/data pairs. C code must use types wide enough for masks such as `0x80000000L` and must handle split address fields correctly on 32-bit and 64-bit builds.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.0 headers and all generation-specific code using these macros; this catches missing, renamed, or malformed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: every register in this range should have matching offset/default entries and field masks that agree with the field width and shift.
- Verify cross-chunk continuity: `BIF_CFG_DEV0_RC1_SLOT_STATUS` must be complete when merged with the previous chunk, and `BIF_BX_PF0_MM_CFGREGS_CNTL` must be complete when merged with the next chunk.
- On affected AMD GPU hardware, exercise PCIe enumeration, bridge bus/window programming, MSI delivery, AER logging, hotplug/status bits where applicable, ACS behavior, link retrain/equalization, suspend/resume, GPU reset, and FLR.
- For AER and interrupt fields, inject or observe correctable/nonfatal/fatal PCIe events and confirm status, masks, root-error reporting, header logs, and source IDs behave as expected.
- For indirect aperture fields, test serialized index/data read and write paths with known registers and verify that unrelated accessors cannot corrupt the selected index.
- For scratch and strap fields, compare driver-observed values with firmware handoff expectations across cold boot, warm reboot, suspend/resume, and GPU reset.
- For repeated lane equalization and DPA allocation registers, include sequence and naming checks in generated-header tests, because simple bit-width checks would not catch swapped lane numbers or duplicated register stems.

## Unresolved Cross-Chunk References

The preceding chunk contains the beginning of `BIF_CFG_DEV0_RC1_SLOT_STATUS`, including the register comment and any field definitions before line 31719. The following chunk contains the remaining `BIF_BX_PF0_MM_CFGREGS_CNTL` mask definitions and subsequent `BIF_BX_PF0_*` BIFDEC1 registers. The final per-file document should stitch these boundaries and summarize the whole `nbio_7_0_sh_mask.h` generated register namespace rather than treating this chunk as a complete header.

### subset-b-003082: lines 34188-36634

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 34188-36634

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,142 `#define` lines across 2,447 source lines: 1,070 `__SHIFT` constants, 1,072 `_MASK` constants, 275 register/address-block comment markers, and no C functions, structs, enums, executable statements, allocations, or locks.

The range starts mid-register with the remaining mask definitions for `BIF_BX_PF0_MM_CFGREGS_CNTL`; the corresponding shift definitions and early masks are in the previous chunk. It then covers BIF PF0 control and status fields, doorbell and HDP apertures, mailbox fields, PCI configuration shadow registers, endpoint/downstream PCIe port control fields for devices 0 and 1, RCC strap/SUM indirect registers, BIF miscellaneous and virtual-wire controls, clock/power-gating/performance-counter fields, GMI arbitration and completion-buffer controls, and the beginning of several RCC PFC decode blocks. The range ends after the first `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL__SNOOP_LATENCY_VALUE__SHIFT` line, so the rest of the USB3_0 PFC LTR register continues in the next chunk.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 register contract. For each hardware field, it exposes:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position used to encode or decode a field.
- `<REGISTER>__<FIELD>_MASK`, the register mask used to isolate, preserve, or update the field.

The companion generated NBIO 7.0 headers provide the other pieces of the same contract: `nbio_7_0_offset.h` for register offsets, `nbio_7_0_smn.h` for SMN addresses, and `nbio_7_0_default.h` for reset/default values. Runtime AMDGPU code combines these constants with register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and related NBIO accessors. This chunk does not implement policy; it names the bits that NBIO, PCIe, interrupt, doorbell, SR-IOV, power-management, and RAS paths can program or decode.

## Important Macro Families

The first group continues BIF PF0 register layouts:

- `BIF_BX_PF0_MM_CFGREGS_CNTL` provides masks for function/device selection and enabling writes through the MM-to-config path.
- `BIF_BX_PF0_BX_RESET_CNTL` exposes `LINK_TRAIN_EN`, which affects link training control.
- `BIF_BX_PF0_INTERRUPT_CNTL` and `BIF_BX_PF0_INTERRUPT_CNTL2` define interrupt-handler dummy-read behavior, non-snoop attributes, interrupt delay counter fields, generic IH interrupt enable, MSI dummy-read bypass behavior, and the dummy-read address.
- `BIF_BX_PF0_CLKREQB_PAD_CNTL`, `BIF_BX_PF0_BIF_PERSTB_PAD_CNTL`, `BIF_BX_PF0_BIF_PX_EN_PAD_CNTL`, `BIF_BX_PF0_BIF_REFPADKIN_PAD_CNTL`, and `BIF_BX_PF0_BIF_CLKREQB_PAD_CNTL` define pad mux/mode/spare/slew/wake/schmitt/control-enable/output fields for PCIe sideband pins.
- `BIF_BX_PF0_BIF_FEATURES_CONTROL_MISC` exposes endpoint request/completion disable bits, ring-buffer overflow behavior, atomic error interrupt disable, non-virtual BME handling, FLR pending-check controls, and a 48-bit self-ring doorbell aperture check bit.
- `BIF_BX_PF0_BIF_DOORBELL_CNTL`, `BIF_BX_PF0_BIF_DOORBELL_INT_CNTL`, `BIF_BX_PF0_BIF_DOORBELL_GBLAPER1_*`, `BIF_BX_PF0_BIF_DOORBELL_GBLAPER2_*`, and `BIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_*` define doorbell translation checks, self-ring behavior, monitor interrupt mode, doorbell/IOHC RAS interrupt status and clears, global aperture lower/upper bounds, and self-ring GPA aperture base/control fields.
- `BIF_BX_PF0_BIF_FB_EN`, `BIF_BX_PF0_BIF_BUSY_DELAY_CNTR`, `BIF_BX_PF0_BIF_MST_TRANS_PENDING_VF`, `BIF_BX_PF0_BIF_SLV_TRANS_PENDING_VF`, and `BIF_BX_PF0_BIF_TRANS_PENDING` describe framebuffer read/write enables, busy-delay counter fields, and master/slave transaction-pending status across VFs and PF-level paths.
- `BIF_BX_PF0_BACO_CNTL` and `BIF_BX_PF0_BIF_BACO_EXIT_TIME0` through `BIF_BX_PF0_BIF_BACO_EXIT_TIMER4` define BACO entry/exit controls, timers, auto-exit behavior, LCLK switching, dummy enable, power-off, sideband timers, hardware auto flush, PX_EN output-enable behavior, and mode selection.
- `BIF_BX_PF0_MEM_TYPE_CNTL`, `BIF_BX_PF0_SMU_BIF_VDDGFX_PWR_STATUS`, `BIF_BX_PF0_BIF_VDDGFX_GFX0_*` through `GFX5_*`, `RSV1_*` through `RSV4_*`, and `BIF_BX_PF0_BIF_VDDGFX_FB_CMP` describe memory-phy selection, VDDGFX power-off status, address lower/upper comparison windows, compare enables, stall enables, and framebuffer compare fields.

The PF/VF mailbox and GPU-IOV groups provide virtualization-facing bit layouts:

- `BIF_BX_PF0_BIF_UVD_GPUIOV_CFG_SIZE`, `BIF_BX_PF0_BIF_VCE_GPUIOV_CFG_SIZE`, and `BIF_BX_PF0_BIF_GFX_SDMA_GPUIOV_CFG_SIZE` hold base/size fields for GPU-IOV configuration regions.
- `BIF_BX_PF0_MAILBOX_INDEX` selects mailbox DW indexing.
- `BIF_BX_PF0_MAILBOX_MSGBUF_TRN_DW0` through `_DW3` and `BIF_BX_PF0_MAILBOX_MSGBUF_RCV_DW0` through `_DW3` define transmit and receive message-buffer data words.
- `BIF_BX_PF0_MAILBOX_CONTROL` defines transmit valid, receive ack, and valid/ack interrupt status/control fields.
- `BIF_BX_PF0_MAILBOX_INT_CNTL` exposes valid and ack interrupt enables.
- `BIF_BX_PF0_BIF_VMHV_MAILBOX` defines a compact VM/HV mailbox with transmit/receive message data, valid/ack flags, and interrupt enables.

The `nbio_nbif0_rcc_shadow_reg_shadowdec` address block mirrors PCI configuration-space shadow fields:

- `SHADOW_COMMAND` tracks upstream IO and memory enable bits.
- `SHADOW_BASE_ADDR_1`, `SHADOW_BASE_ADDR_2`, `SHADOW_SUB_BUS_NUMBER_LATENCY`, `SHADOW_IO_BASE_LIMIT`, `SHADOW_MEM_BASE_LIMIT`, `SHADOW_PREF_BASE_LIMIT`, `SHADOW_PREF_BASE_UPPER`, `SHADOW_PREF_LIMIT_UPPER`, `SHADOW_IO_BASE_LIMIT_HI`, and `SHADOW_IRQ_BRIDGE_CNTL` define BAR, bus-number, IO/memory/prefetchable-window, VGA/ISA decode, and secondary-bus reset fields.
- `SUC_INDEX` and `SUC_DATA` provide an indexed register/data pair for shadow/SUC access.

The RCC endpoint and downstream port blocks describe PCIe port control and error behavior:

- `RCC_EP_DEV0_1_*` and `RCC_EP_DEV1_*` endpoint registers include scratch fields, unsupported-request reporting controls, malformed atomic handling, interrupt enables/status bits for correctable/non-fatal/fatal/user/misc/power-state events, invalid-PASID ignore behavior, immediate PMI disable, hidden config decode enables, TX LTR controls, DPA capability/latency/control/substate power allocation, PME service timer, TX SNR/RO/TPH fields, requester ID composition, AER header-log timeout/expired bits, error-message control, RX ignore controls for payload/TC/prefix/PASID/TPH/completion timeout, and Gen2/Gen3 speed strap fields.
- `RCC_DWN_DEV0_1_*` and `RCC_DWN_DEV1_*` downstream registers include reserved/scratch fields, hardware-init write lock, unsupported-request reporting disable, LTR-message UR ignore, extended tag override, FLR extend mode, immediate PMI disable, AER completion timeout read-only behavior, and hidden config decode enables.
- `RCC_DWNP_DEV0_1_*` and `RCC_DWNP_DEV1_*` downstream-port registers define error reporting, AER header-log timeout/status, immediate error message send, RX ignore controls, RCB FLR timeout disable, Gen2/Gen3 link speed strap fields, link-bandwidth notification disable, multi-function strap, and received endpoint LTR message information.
- `RCC_STRAP1_RCC_DEV0_EPF0_STRAP0` exposes dev0 EP function strap fields, while `SUM_INDEX` and `SUM_DATA` provide another indexed register/data pair in the BIF PF summary decoder.

The `nbio_nbif0_bif_misc_bif_misc_regblk` address block covers miscellaneous NBIF/BIF control:

- `MISC_SCRATCH`, `INTR_LINE_POLARITY`, `INTR_LINE_ENABLE`, and `OUTSTANDING_VC_ALLOC` provide scratch, interrupt-line polarity/enable, and virtual-channel allocation fields.
- `BIFC_MISC_CTRL0`, `BIFC_MISC_CTRL1`, `BIFC_BME_ERR_LOG`, and `BIFC_RCCBIH_BME_ERR_LOG` define BIF-side control and bus-master-enable error logging/clear bits across dev0/dev1 functions.
- `BIFC_DMA_ATTR_OVERRIDE_DEV0_F0_F1` through `DEV0_F6_F7` and `BIFC_DMA_ATTR_OVERRIDE_DEV1_F0_F1` through `DEV1_F6_F7` define per-function posted/non-posted DMA attribute overrides for IDO, relaxed ordering, and snoop/no-snoop behavior.
- `NBIF_VWIRE_CTRL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL`, `NBIF_SMN_VWR_VCHG_RST_CTRL0`, `NBIF_SMN_VWR_VCHG_TRIG`, `NBIF_SMN_VWR_WTRIG_CNTL`, `NBIF_SMN_VWR_VCHG_DIS_CTRL_1`, `NBIF_SDP_VWR_VCHG_DIS_CTRL`, `NBIF_SDP_VWR_VCHG_RST_CTRL0`, `NBIF_SDP_VWR_VCHG_RST_CTRL1`, and `NBIF_SDP_VWR_VCHG_TRIG` define virtual-wire reset delays, posted/block-level behavior, voltage-change set disable/reset-default/trigger bits, and write-trigger controls.
- `NBIF_MGCG_CTRL_LCLK`, `NBIF_DS_CTRL_LCLK`, `BME_DUMMY_CNTL_0`, `BIFC_THT_CNTL`, `BIFC_HSTARB_CNTL`, `BIFC_GSI_CNTL`, `BIFC_PCIEFUNC_CNTL`, `BIFC_SDP_CNTL_0`, `BIFC_SDP_CNTL_1`, `NBIF_REGIF_ERRSET_CTRL`, `NBIF_PGMST_CTRL`, `NBIF_PGSLV_CTRL`, and `NBIF_PG_MISC_CTRL` define LCLK clock-gating/deep-sleep controls, BME dummy behavior, throttle/host arbitration/GSI/PCIe function controls, SDP controls, register-interface error-set behavior, and master/slave/misc power-gating bits.
- `SMN_MST_CNTL0`, `SMN_MST_CNTL1`, and `SMN_MST_EP_CNTL1` through `SMN_MST_EP_CNTL5` define SMN master/endpoint control fields.
- `BIFC_PERF_CNTL_0`, `BIFC_PERF_CNTL_1`, `BIFC_PERF_CNT_MMIO_RD`, `BIFC_PERF_CNT_MMIO_WR`, `BIFC_PERF_CNT_DMA_RD`, and `BIFC_PERF_CNT_DMA_WR` expose BIF performance-counter control and count fields for MMIO and DMA read/write traffic.
- `BIF_SELFRING_BUFFER_VID`, `BIF_SELFRING_VECTOR_CNTL`, `BIF_GMI_WRR_WEIGHT`, `BIF_GMI_CPLBUF_WR_CTRL`, and `BIF_GMI_CPLBUF_RD_CTRL` define self-ring buffer/vector fields, GMI weighted-round-robin request weights/mode, and completion-buffer reservation controls per VC.

The RCC PFC blocks at the end repeat a compact per-function controller layout:

- `RCC_PFC_AMDGFX_*`, `RCC_PFC_AMDGFXAZ_*`, and `RCC_PFC_PSP_*` define LTR snoop/non-snoop latency value/scale/requirement fields, PME restore enable/status, sticky PCIe error-status restore bits, restored TLP header/prefix DWs, and auxiliary-power override fields.
- `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL` starts at the chunk boundary with `SNOOP_LATENCY_VALUE__SHIFT`; the remaining USB3_0 PFC fields are outside this chunk.

## APIs, Types, And Functions

There are no callable APIs or local C types in this range. The public interface is the generated macro namespace. Consumers depend on the exact spelling and value of each register/field shift and mask.

The constants are untyped preprocessor integer literals. Masks generally use an `L` suffix and range from byte/word-sized fields to full `0xFFFFFFFFL` register fields. They encode field placement only. They do not describe access permissions, reset domains, polling delays, side effects, clear-on-write behavior, hardware ownership, firmware ownership, or whether a field is configuration, command, sticky status, latched status, or reserved. Those semantics must come from the hardware specification and the AMDGPU call site using the macros.

## Control Flow

This header segment has no local control flow. Runtime flow is external:

1. AMDGPU code selects an NBIO/SMN/PCIe register address from `nbio_7_0_offset.h` or `nbio_7_0_smn.h`.
2. The code reads the register, decodes fields with these `__SHIFT`/`_MASK` constants, or composes an updated value with register-field helpers.
3. The resulting value is written back to hardware, used to poll status, used to clear latched interrupt/error state, or used as input to PCIe, doorbell, interrupt, power-management, SR-IOV, or RAS policy.

Likely runtime flows involving these field families include NBIO initialization, PCIe link training and speed/hidden-config setup, interrupt routing through IH/MSI paths, HDP flush/coherency handling, doorbell aperture programming, BACO entry/exit, VDDGFX power gating and address-stall comparison, PF/VF mailbox exchange, GPU-IOV aperture configuration, PCIe endpoint/downstream error handling, AER/status restoration after power events, virtual-wire voltage-change signaling, LCLK clock gating/deep sleep, BIF performance sampling, and GMI arbitration tuning.

## State And Persistence Behavior

The header itself stores no state. It names NBIO 7.0 hardware-visible state. Persistence is determined by the hardware reset domain, BACO and power-gating transitions, SMU/firmware/BIOS initialization, driver suspend/resume restore, SR-IOV PF/VF ownership, and explicit register writes.

Represented state includes interrupt dummy-read policy, doorbell and self-ring aperture bounds, FB read/write enables, BIF transaction-pending status, BACO timers and mode bits, VDDGFX power/status and address compare windows, HDP coherency/flush controls, mailbox transmit/receive buffers and valid/ack flags, PCI config shadow windows, PCIe endpoint/downstream error enables/status/ignore controls, DPA/PME/LTR fields, BME error logs and clear bits, per-function DMA attribute overrides, virtual-wire voltage-change triggers, clock-gating and power-gating controls, performance counter values, GMI WRR weights, PFC sticky restore state, and PFC restored TLP header/prefix fields.

Several fields are not passive storage. Link-training, interrupt-enable, interrupt-clear, doorbell aperture, BACO, VDDGFX stall, HDP flush, mailbox valid/ack, AER error, BME clear, virtual-wire trigger, clock/power-gating, performance-counter control, and LTR/PME fields can directly affect live device behavior or observable OS/firmware state. Full-register writes should preserve unrelated and reserved fields unless the hardware sequence explicitly requires a literal value.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.0 register database and must stay aligned with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h`

Direct include users in this source tree include `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`, and NBIO 7.x runtime code such as `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` uses the same generated-register pattern for HDP remap, memory-controller access, doorbells, interrupt control, clock gating, light sleep, PCIe index/data accessors, register initialization, and register remapping. RAS code for newer NBIO 7.x revisions uses related NBIO register infrastructure for controller and error-event interrupts.

Although this repository path is under a `ceph-client` source tree, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem logic.

## Risks And Edge Cases

- Generated shift/mask drift can compile successfully while making the driver program or decode the wrong NBIO bits. The most sensitive fields in this chunk affect link training, interrupts, doorbell apertures, HDP flush/coherency, BACO, VDDGFX power gating, mailbox handshakes, PCIe error handling, virtual-wire triggers, and clock/power gating.
- The chunk starts mid-register at `BIF_BX_PF0_MM_CFGREGS_CNTL` masks and ends mid-register-family at `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL`; adjacent chunks are required for complete per-register coverage.
- Many register families are repeated by device, function pair, or endpoint/downstream block. Repetition is intentional, but a single field-width mismatch between `DEV0` and `DEV1` or between endpoint/downstream variants may indicate generator or register-database drift.
- Mailbox valid/ack and interrupt status/clear bits can be edge-sensitive or handshake-sensitive. Incorrect masks can cause lost PF/VF messages, stuck interrupts, or virtualization deadlocks.
- Doorbell and self-ring aperture fields define address acceptance and translation behavior. Wrong bounds or enable/check bits can route writes to the wrong engine, block valid queues, or expose an aperture beyond the intended range.
- BACO and VDDGFX fields control live power transitions. Incorrect timer, auto-exit, power-off, stall, or compare-window programming can break suspend/resume, reset, or low-power idle transitions.
- PCIe error mask/ignore fields can hide real protocol errors or generate error storms. AER header-log and sticky restore fields may be latched, clear-on-write, or firmware-managed.
- Virtual-wire voltage-change trigger/reset fields and clock/power-gating controls can interact with SMU/firmware sequencing; read-modify-write preservation is important for unrelated sets and reserved bits.

## Test Signals

- Build AMDGPU with NBIO 7.0/SMU10 support enabled. Direct macro users catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: offset/default/shift/mask name alignment, mask-width validation, non-overlap checks within each register, and repetition checks across device/function variants.
- Validate adjacent chunk boundaries: `BIF_BX_PF0_MM_CFGREGS_CNTL` should become complete with the previous chunk, and `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL` should continue cleanly in the next chunk.
- On NBIO 7.0 hardware, boot tests should show stable PCIe link training, correct negotiated width/speed, no unexpected AER storms, working interrupts, and functional doorbell-backed queues.
- Runtime suspend/resume, BACO, and reset tests should verify doorbell aperture restore, HDP flush/coherency behavior, BACO exit timing, VDDGFX status/compare behavior, and PCIe endpoint/downstream status restoration.
- SR-IOV smoke tests should exercise PF/VF mailbox valid/ack interrupts, GPU-IOV configuration sizes, per-function DMA attribute overrides, and transaction-pending status.
- RAS/error-injection or lab diagnostics should confirm BME error logs/clear bits, PCIe AER header-log fields, PFC sticky restore fields, and doorbell/IOHC RAS interrupt status/clear behavior.
- Power-management validation should cover LCLK MGCG/deep-sleep controls, virtual-wire voltage-change triggers, SMN/SDP virtual-wire reset behavior, and performance-counter readout stability.

### subset-b-003083: lines 36635-39058

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 36635-39058

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It spans 2,424 source lines and contains 2,150 `#define` lines: 1,075 `__SHIFT` constants and 1,075 `_MASK` constants across 245 register names. There are no C functions, structs, enums, global variables, allocation sites, locks, or executable statements in this range.

The range starts mid-register in `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL`: line 36634, immediately before this chunk, defines `SNOOP_LATENCY_VALUE__SHIFT`, while this chunk starts at `SNOOP_LATENCY_SCALE__SHIFT` and includes the remaining shifts and all masks for that register. It then covers the rest of the USB3_0 RCC PFC restore/auxiliary-power fields, complete RCC PFC blocks for USB3_1, ACP, AZ, MP2, SATA, GBE0, and GBE1, the NBIF0 BIF reset register block, the NBIF0 BIF RAS register block, and the beginning of the `BIF_CFG_DEV0_EPF0_2` PCI/PCIe endpoint configuration-space field layout through `PCIE_BAR2_CNTL`. The next chunk is needed for `PCIE_BAR3_*` and later endpoint capability definitions.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 hardware register contract. Each field is represented by a pair of preprocessor constants:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position for encoding or decoding a field.
- `<REGISTER>__<FIELD>_MASK`, the mask that isolates or preserves that field in the containing register.

Runtime code combines these definitions with companion generated address/default headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and related SOC15/NBIO accessors. This header does not decide when hardware is touched. It gives NBIO v7.0 driver code the named bit positions for PCIe-facing power management, reset, RAS/error handling, interrupt status/masking, function-level reset, D-state tracking, MSI/MSI-X, AER, virtual-channel, BAR, and endpoint configuration fields.

Although this repository path sits under a `ceph-client` source mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem behavior.

## Important Macro Families

The RCC PFC blocks describe per-client PCIe/Root Complex Configuration power-management and restore fields:

- `RCC_PFC_USB3_0_*` starts in the previous line and continues here with LTR scale/requirement fields, PME restore, sticky PCIe error restore, captured TLP header/prefix restore, and auxiliary-power override fields.
- `RCC_PFC_USB3_1_*`, `RCC_PFC_ACP_*`, `RCC_PFC_AZ_*`, `RCC_PFC_MP2_*`, `RCC_PFC_SATA_*`, `RCC_PFC_GBE0_*`, and `RCC_PFC_GBE1_*` repeat the same register pattern for additional clients.
- `RCC_PFC_*_RCC_PFC_LTR_CNTL` defines snoop and non-snoop latency value, scale, and requirement bits. These fields model PCIe Latency Tolerance Reporting programming for the client.
- `RCC_PFC_*_RCC_PFC_PME_RESTORE` preserves PME enable/status state across the relevant power/reset event.
- `RCC_PFC_*_RCC_PFC_STICKY_RESTORE_0` through `_5` expose sticky AER-style error status and captured TLP header/prefix restore fields, including poisoned TLP, completion timeout/abort, unexpected completion, malformed TLP, ECRC, unsupported request, and advisory non-fatal status.
- `RCC_PFC_*_RCC_PFC_AUXPWR_CNTL` exposes auxiliary-current and auxiliary-power-detected override fields.

The BIF reset block defines NBIO reset policy, reset causes, reset interrupt state, and per-function reset/D-state fields:

- `HARD_RST_CTRL`, `RSMU_SOFT_RST_CTRL`, and `SELF_SOFT_RST` define reset-enable masks for dispatch/config, endpoint config/private state, shadow/sticky state, strap reload, and core reset domains. `SELF_SOFT_RST` also exposes self reset trigger and grant/request style fields.
- `BIF_GFX_DRV_VPU_RST` names VPU/GFX driver reset handshake bits, including reset request, interrupt, timeout, and related mask/status controls.
- `BIF_RST_MISC_CTRL`, `BIF_RST_MISC_CTRL2`, and `BIF_RST_MISC_CTRL3` define miscellaneous reset behavior such as reset selection, clock-domain handling, FLR/D-state behavior, and debug/status controls.
- `DEV0_PF0_FLR_RST_CTRL` through `DEV0_PF7_FLR_RST_CTRL` and `DEV1_PF0_FLR_RST_CTRL` through `DEV1_PF7_FLR_RST_CTRL` describe function-level reset controls and status for two devices and up to eight physical functions each. PF0 on device 0 has the widest field set; the other PFs follow the compact completion/ack/reset-status pattern.
- `BIF_INST_RESET_INTR_STS`, `BIF_PF_FLR_INTR_STS`, `BIF_D3HOTD0_INTR_STS`, `BIF_POWER_INTR_STS`, and `BIF_PF_DSTATE_INTR_STS` define reset, FLR, D3hot-to-D0, power, and D-state interrupt status fields. Matching `_MASK` registers define the corresponding interrupt masks.
- `BIF_PF_FLR_RST` supplies PF reset command/status bits.
- `BIF_DEV0_PF*_DSTATE_VALUE`, `BIF_DEV1_PF*_DSTATE_VALUE`, `BIF_PORT0_DSTATE_VALUE`, and `BIF_PORT1_DSTATE_VALUE` expose saved or observed power-state values.
- `DEV0_PF*_D3HOTD0_RST_CTRL` and `DEV1_PF*_D3HOTD0_RST_CTRL` control reset behavior around D3hot-to-D0 transitions.

The BIF RAS block defines register fields for Reliability, Availability, and Serviceability handling:

- `BIF_RAS_LEAF0_CTRL`, `BIF_RAS_LEAF1_CTRL`, and `BIF_RAS_LEAF2_CTRL` name per-leaf RAS enable, status, inject, and mask-style fields for BIF error reporting paths.
- `BIF_RAS_MISC_CTRL`, `BIF_IOHUB_RAS_IH_CNTL`, and `BIF_RAS_VWR_FROM_IOHUB` add miscellaneous BIF RAS controls and IOHUB interrupt/vector-window integration fields.

The `BIF_CFG_DEV0_EPF0_2_*` block mirrors a PCI/PCIe endpoint configuration space and extended capability layout:

- Basic PCI configuration fields include `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `_6`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, min-grant/max-latency, and vendor/adapter ID write paths.
- Power-management capability fields include `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` for capability ID/version/next pointer, D-state support, PME support, current power state, PME enable/status, data select, and bridge-extension status.
- PCIe capability fields include `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, and the slot-capability placeholders. These fields model maximum payload/read request size, relaxed ordering, no-snoop, FLR initiation, link speed/width, ASPM/L0s/L1 controls, link retraining, clock power management, completion timeout controls, atomic operation support, OBFF, LTR, emergency power reduction, and related PCIe status bits.
- MSI/MSI-X fields include `MSI_CAP_LIST`, `MSI_MSG_CNTL`, message address/data/mask/pending registers for 32-bit and 64-bit variants, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Vendor-specific and virtual-channel capability fields include `PCIE_VENDOR_SPECIFIC_*`, `PCIE_VC_ENH_CAP_LIST`, port VC capability/control/status fields, and VC0/VC1 resource capability/control/status fields.
- Device serial number fields include `PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `PCIE_DEV_SERIAL_NUM_DW1`, and `DW2`.
- Advanced Error Reporting fields include `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, header logs `PCIE_HDR_LOG0` through `_3`, and TLP prefix logs `PCIE_TLP_PREFIX_LOG0` through `_3`.
- The chunk ends with the enhanced BAR capability header plus `PCIE_BAR1_CAP`, `PCIE_BAR1_CNTL`, `PCIE_BAR2_CAP`, and `PCIE_BAR2_CNTL`. BAR3 and later BAR/power-budget capability fields continue after this range.

## APIs, Types, And Functions

There are no local callable APIs or type declarations in this chunk. The interface is the generated macro namespace. Consumers rely on exact symbol names, shifts, and masks being synchronized with the corresponding NBIO v7.0 offset/default headers and with the underlying hardware register database.

The constants are untyped preprocessor integer literals. Many masks use an `L` suffix and may represent 16-bit PCI configuration fields or 32-bit NBIO registers depending on the containing register. The macros encode field placement only. They do not encode access width, read/write permissions, reset domain, required ordering, delays, polling semantics, clear-on-write behavior, firmware ownership, or whether a bit is command, live status, latched status, sticky status, or reserved. Those properties must come from the hardware specification and from the AMDGPU call site using the fields.

## Control Flow

This header segment has no local control flow. Runtime flow is external:

1. AMDGPU NBIO, SOC15, PCIe, power-management, reset, or virtualization code selects a register address from generated offset/SMN headers.
2. The code reads a register and decodes fields with these shifts and masks, or composes a new value with register-field helpers.
3. The resulting value is written back to hardware, used to poll status, used to preserve/restore state, or used to report PCIe/RAS/reset information upward.

Likely runtime flows involving this chunk include LTR programming for on-chip PCIe clients, PME and sticky-error restore across power events, FLR and D3hot-to-D0 reset sequencing, GPU/NBIO hard and soft reset paths, reset interrupt masking and acknowledgement, per-PF D-state tracking, BIF RAS enable/status/masking, PCI configuration setup, PCIe link capability/control handling, MSI/MSI-X setup, AER status collection and masking, virtual-channel configuration, device serial number exposure, and BAR capability sizing/control.

## State And Persistence Behavior

The header stores no software state. It names hardware-visible state in NBIO v7.0 RCC PFC, BIF reset, BIF RAS, and endpoint configuration registers. Persistence is determined by PCIe reset type, NBIO reset domains, BIOS/firmware initialization, runtime power management, suspend/resume restore flows, SR-IOV PF/VF ownership, and explicit driver writes.

Represented persistent or semi-persistent state includes LTR values, PME enable/status restore state, sticky AER restore bits, captured TLP header/prefix logs, auxiliary power override state, reset-enable policy, FLR/D3hot-to-D0 control, interrupt mask settings, PF D-state values, RAS enable/mask/inject/status bits, PCI command/status fields, BAR controls, MSI/MSI-X table and masking controls, PCIe device/link capability/control fields, AER error masks/severity, and AER header/TLP-prefix logs.

Several fields are not passive storage. Reset request/enable bits, `INITIATE_FLR`, D3hot-to-D0 reset controls, RAS injection bits, PME status, interrupt status bits, AER status bits, and MSI/MSI-X mask/pending controls can have side effects or hardware-defined clear semantics. Full-register writes are risky unless the caller intentionally owns every bit in the target register; read-modify-write with the generated masks is normally the safer pattern for mixed control/status/reserved registers.

## Dependencies And Integration Points

This chunk depends on the generated NBIO v7.0 register database and must stay aligned with companion generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h` for matching register offsets.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h` for SMN-addressed register names where applicable.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h` for reset/default values.

Direct include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Those users pull this generated mask namespace into NBIO v7.0 initialization, SOC15 device handling, and SMU10 power-management register programming. The endpoint configuration symbols also integrate with generic PCIe concepts: command/status setup, link configuration, power management, MSI/MSI-X, AER, virtual channels, serial-number capability, and BAR sizing/control.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing driver code to set or decode the wrong hardware bit. The highest-impact fields here are reset controls, FLR/D3hot-to-D0 paths, PCIe command/device/link controls, MSI/MSI-X mask and pending fields, and AER status/mask/severity fields.
- The source range starts mid-register. A reader needs the previous line for the complete `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL` shift set.
- The range ends before BAR3 and later endpoint capability fields. A merged per-file document should treat this as the first half of the `BIF_CFG_DEV0_EPF0_2` extended capability layout, not the whole endpoint config block.
- RCC PFC blocks are intentionally repetitive across USB3, ACP, AZ, MP2, SATA, and GBE clients. A mismatched field width or mask pattern could be a real per-client hardware difference, but it is also a strong signal to verify generator output.
- Reset registers mix command, enable, status, sticky, and interrupt fields. Incorrect writes can leave a PF stuck in reset, miss FLR completion, clear a diagnostic status too early, or trigger an unintended NBIO/core reset.
- PCIe capability/control fields include negotiated link width/speed, ASPM, clock power management, completion timeout, atomic operations, LTR, OBFF, and FLR initiation. Bad programming can show up as link training failures, AER storms, failed resume, performance loss, or device disappearance.
- AER and sticky-restore fields represent latched error state and captured TLP/header context. Wrong masks can hide real PCIe faults or produce misleading error reports.
- MSI/MSI-X mask/pending fields are interrupt-critical. Incorrect bit positions can cause lost interrupts, interrupt storms, or incorrect interrupt affinity/debugging conclusions.
- RAS injection and status fields should be treated as lab or controlled-validation surfaces unless the caller is explicitly handling BIF RAS test flows.
- Reserved or undocumented bits are not modeled by separate macros. Callers should preserve them unless a hardware sequence explicitly requires a literal write.

## Test Signals

- Build AMDGPU with NBIO v7.0/SOC15 and SMU10 support enabled. Direct include users catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO v7.0 register database: register-name alignment across offset/default/shift/mask headers, mask-width checks, non-overlap checks within each register, and repeated-client consistency checks for RCC PFC blocks.
- Verify chunk boundaries during merge: `RCC_PFC_USB3_0_RCC_PFC_LTR_CNTL` should include the missing first shift from the previous line, and `BIF_CFG_DEV0_EPF0_2_PCIE_BAR3_*` should continue immediately after this chunk.
- On NBIO v7.0 hardware, boot and suspend/resume tests should show stable PCIe enumeration, expected BAR sizing, expected MSI/MSI-X behavior, no unexpected AER storms, and stable negotiated link width/speed.
- Exercise FLR, GPU reset, D3hot-to-D0, runtime suspend, and system suspend flows while checking that reset interrupts are delivered/masked/cleared as expected and PF D-state values are sane.
- Validate PCIe power-management paths that use LTR, ASPM, clock power management, PME, and auxiliary-power fields.
- RAS validation should cover BIF RAS enable/mask/status paths and controlled injection where supported, with expected interrupt routing through IOHUB handling.
- PCIe error tests should verify uncorrectable/correctable AER status, mask, severity, header log, and TLP prefix log decoding against known error injections or platform traces.

### subset-b-003084: lines 39059-41512

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 39059-41512

## Scope

This chunk is a generated register bitfield header segment for AMD NBIO 7.0 PCIe/NBIF configuration space. It contains 2,095 `#define` entries and 357 register/comment markers. The definitions are all preprocessor constants of the form `<register>__<field>__SHIFT` and `<register>__<field>_MASK`, used by AMDGPU register helpers such as `REG_GET_FIELD()`, `REG_SET_FIELD()`, `WREG32_FIELD15()`, `RREG32_PCIE()`, `WREG32_PCIE()`, and SOC15 offset/index accessors.

The chunk has two major regions:

- Lines 39059-40006 finish the `BIF_CFG_DEV0_EPF0_2_*` PCIe configuration block, beginning mid-way through its BAR capability/control definitions and continuing through SR-IOV and AMD GPU IOV vendor-specific fields.
- Lines 40008-41512 start `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` and define the beginning of the `BIF_CFG_DEV0_EPF1_1_*` PCI configuration block through `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW1`.

## Purpose

The header gives the driver named masks and shift values for fields inside NBIO 7.0 PCI/PCIe configuration registers. The constants make register access code self-documenting and reduce hard-coded bit arithmetic in AMDGPU platform code. The source is not executable and has no functions, types, static storage, or runtime control flow by itself; its behavior is realized when included by C files that read, write, or decode NBIO/PCIe registers.

This particular chunk is centered on PCIe endpoint function configuration. It covers BAR sizing, power budget and dynamic power allocation, link equalization, access/security services, address translation, page requests, PASID, TPH requester, multicasting, latency tolerance reporting, ARI, SR-IOV, and AMD vendor-specific GPU IOV state and mailbox fields. It also begins a second endpoint/function namespace with conventional PCI config header fields, PCIe capabilities, MSI/MSI-X, virtual channels, device serial number, advanced error reporting, BARs, and the same advanced PCIe/SR-IOV/GPU-IOV facilities.

## Important Register Families

### `BIF_CFG_DEV0_EPF0_2_*`

The `EPF0_2` region starts at `PCIE_BAR3_CAP` and includes:

- BAR capability/control registers for BAR3 through BAR6. Each BAR capability exposes `BAR_SIZE_SUPPORTED`; each BAR control exposes `BAR_INDEX`, `BAR_TOTAL_NUM`, and `BAR_SIZE`.
- PCIe power budget extended capability fields: enhanced capability header, data selector, base power, scale, PM state/substate, type, power rail, and system-allocation state.
- PCIe Dynamic Power Allocation fields: DPA capability, latency indicator, status/control, and substate power allocations 0-7.
- Secondary PCIe capability fields including link control 3 and per-lane error/equalization registers for lanes 0-15. Each lane equalization register has downstream/upstream TX preset and RX preset hint fields plus reserved bits.
- Access Control Services: enhanced capability header, ACS capability bits (`SOURCE_VALIDATION_CAP`, `TRANSLATION_BLOCKING_CAP`, P2P redirect/completion/upstream/egress/direct-translated-P2P capabilities), and matching ACS control enables.
- ATS, Page Request Interface, PASID, and TPH requester capability/control fields used by IOMMU/SVM and PCIe requester features.
- Multicast capability/control/address/receive/blocking fields.
- LTR and ARI capability/control fields.
- SR-IOV capability/control/status and sizing/addressing fields: initial/total/current VFs, dependency link, first VF offset, VF stride, VF device ID, supported/system page sizes, VF BAR base addresses 0-5, and VF migration-state array offset.
- AMD GPU IOV vendor-specific extended capability fields: VSEC header, SR-IOV shadow, interrupt enable/status bits for GFX/UVD/VCE completion, hang recovery, FLR-needed, VM-busy transitions, and HVVM mailbox events.
- GPU IOV mailbox and resource accounting fields: `HVVM_MBOX_DW0` through `DW2`, context, total framebuffer, offset layout, per-VF framebuffer ranges for VF0-VF15, UVD/VCE/GFX scheduler dwords 0-8.

### `BIF_CFG_DEV0_EPF1_1_*`

The `EPF1_1` region begins with an explicit address block marker and then defines a separate PCI function's config space fields:

- Standard PCI header fields: vendor/device ID, command, status, revision/program interface/subclass/base class, cache line, latency, header, BIST, base address registers 1-6, adapter ID, ROM base, capability pointer, interrupt line/pin, and min/max latency/grant.
- Power management capability and status/control fields, including PME clock/version, D-state support, PME support, power/data scale/value, PME enable/status, and data select/scale.
- PCIe capability, device capability/control/status, link capability/control/status, device/link capability/control/status 2, and slot 2 placeholders. These fields describe max payload, phantom functions, L0s/L1 latency, role/error reporting controls, relaxed ordering, no-snoop, extended tags, FLR, completion timeout, atomic operations, OBFF, LTR, target link speed, equalization status, and related PCIe link behavior.
- MSI and MSI-X capability fields: capability IDs/pointers, message enable/count, 64-bit and per-vector-mask flags, MSI address/data/mask/pending fields, MSI-X table and PBA BIR/offset fields.
- PCIe vendor-specific capability header and two vendor-specific data registers.
- Virtual channel capability/control/status and VC0/VC1 resource capability/control/status fields.
- Device serial number and Advanced Error Reporting fields: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, and TLP prefix logs.
- BAR capability/control for BAR1-BAR6 and the same power budget, DPA, secondary PCIe, per-lane equalization, ACS, ATS, page request, PASID, TPH, multicast, LTR, ARI, SR-IOV, and GPU IOV groups seen in `EPF0_2`, through `GPUIOV_HVVM_MBOX_DW1`.

## APIs, Types, and Functions

This chunk defines no C APIs, structs, enums, or functions. Its API surface is the macro namespace consumed by AMDGPU code and by other generated register headers. The important contract is macro naming consistency:

- `__SHIFT` constants provide the bit offset for a register field.
- `_MASK` constants provide the positioned mask for the same field.
- The register name segment must match the second argument expected by `REG_GET_FIELD(value, REG, FIELD)` and `REG_SET_FIELD(value, REG, FIELD, field_value)`.
- The register-level address constants are not in this chunk; they are supplied by companion headers such as `nbio_7_0_offset.h` and `nbio_7_0_smn.h`.

Direct include users observed in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. `nbio_v7_0.c` uses the generated NBIO mask/header set for NBIO initialization, PCIe indirect index/data offsets, HDP flush registers, doorbell aperture ranges, clock gating, light sleep, memory controller access, and interrupt handling. `soc15.c` includes the same header set while composing SOC15 IP blocks and PCIe performance/link helpers. The SMU include path exposes the register macros to power-management code.

## Control Flow and Data Flow

There is no local control flow. Downstream control flow is indirect:

1. AMDGPU code selects an NBIO register address through `SOC15_REG_OFFSET(...)`, an SMN address, or PCIe index/data helpers.
2. The driver reads a 32-bit register value, updates fields with the `__SHIFT`/`_MASK` macros, and writes it back; or it reads a value and decodes fields for status/debug behavior.
3. Hardware persists or reports the corresponding PCIe/NBIO state until reset, link retraining, FLR, power transition, firmware action, or another driver/hypervisor write changes it.

Because this chunk includes PCI config capability structures, some fields represent software-visible PCI configuration state rather than normal MMIO-only state. Fields like MSI/MSI-X, command/status, BARs, SR-IOV control, ACS/ATS/PASID/PRI controls, and AER masks/status are externally meaningful to Linux PCI core, IOMMU code, virtualization layers, and platform firmware/hypervisor policy.

## State and Persistence Behavior

The macros have no persistence, but the registers they describe are persistent hardware state for the current device lifetime. Important state classes include:

- Link training and quality state: lane error status, equalization control, link status/control, speed/width fields, and equalization phase/completion bits.
- Address decoding state: standard BARs, enhanced BAR sizing controls, ROM base address, VF BAR base registers, and SR-IOV page-size/stride/offset fields.
- Interrupt routing state: MSI/MSI-X message controls, masks, pending bits, and GPU IOV vendor-specific interrupt enable/status bits.
- Virtualization state: SR-IOV enable/MSE/ARI hierarchy, VF counts, VF migration state array offsets, GPU IOV VF enable/count shadow, VF framebuffer allocations, scheduler dwords, and HVVM mailbox ack/valid bits.
- Error handling state: AER uncorrectable/correctable status, mask, severity, header log, TLP prefix log, and FLR-related vendor reset control.
- IOMMU/SVM-facing state: ACS, ATS, Page Request, PASID, TPH, and multicast capability/control fields.
- Power/link policy state: PM capability/status, power budget data, DPA controls/substates, LTR latency fields, and link control fields.

Some status registers are likely write-one-to-clear or hardware-updated according to PCIe semantics, but this header does not encode access policy. Call sites must rely on the hardware specification, PCI core rules, or existing AMDGPU helpers before writing a mask back.

## Dependencies and Integration Points

This chunk depends on the rest of the generated NBIO 7.0 register set:

- `nbio_7_0_offset.h` for MMIO/config register address constants.
- `nbio_7_0_smn.h` for SMN addresses used by `RREG32_PCIE()`/`WREG32_PCIE()` paths.
- `nbio_7_0_default.h` for reset/default values.
- AMDGPU register helper macros that concatenate `REG__FIELD_MASK` and `REG__FIELD__SHIFT`.

The runtime integration points are broader than the direct symbol references suggest. The fields map to hardware-visible PCIe capability layouts, so any driver, kernel PCI subsystem path, guest VF driver, hypervisor, firmware component, or diagnostic tool that reads/writes the corresponding config space is part of the behavioral contract. The AMDGPU side of that contract appears through NBIO setup (`nbio_v7_0_funcs`), SOC15 device bring-up, power management include paths, interrupt programming, PCIe performance counters, and virtualization support such as SR-IOV/MxGPU.

## Risks

- Field drift from hardware XML/specification would silently corrupt register manipulation because `REG_SET_FIELD()` composes writes from these constants. A wrong mask or shift can affect adjacent reserved or control bits.
- The chunk crosses from `EPF0_2` into `EPF1_1`; copy/paste or generation errors can easily produce a correct-looking macro name in the wrong endpoint/function namespace.
- ACS/ATS/PRI/PASID/SR-IOV fields are security-sensitive. Incorrect masks can weaken DMA isolation, peer-to-peer routing controls, address translation, VF enablement, or VF BAR exposure.
- MSI/MSI-X and vendor-specific interrupt fields are interrupt-routing sensitive. Wrong masks can drop completion/hang/FLR mailbox notifications or produce spurious interrupts.
- AER status/mask/severity fields are reliability-sensitive. Incorrect error masks can hide fatal link/device errors or over-report correctable errors.
- GPU IOV fields are hypervisor/guest contract fields. VF framebuffer ranges, scheduler dwords, HVVM mailbox ack/valid bits, and VF count/enable shadows must line up with firmware and virtualization manager expectations.
- Reserved-bit masks appear in several registers. Call sites must avoid writing arbitrary values through reserved masks unless the hardware programming guide requires it.
- Many fields are duplicated across endpoint/function namespaces. Search/replace use can accidentally mix `BIF_CFG_DEV0_EPF0_2_*` and `BIF_CFG_DEV0_EPF1_1_*`.

## Test and Validation Signals

Useful signals for changes to this chunk are mostly compile-time, boot-time, and hardware/virtualization validation:

- Build AMDGPU configurations that include SOC15/NBIO 7.0 and SMU10 paths; macro name mismatches surface as compile errors in `nbio_v7_0.c`, `soc15.c`, and power-management includes.
- Exercise GPU boot/resume/reset on NBIO 7.0 ASICs and check that NBIO init, HDP flush, doorbells, interrupt setup, clock gating, and light sleep still work.
- Inspect PCI config space with `lspci -vvv` for expected capabilities: AER, ACS, ATS, PRI, PASID, LTR, ARI, SR-IOV, MSI/MSI-X, and vendor-specific GPU IOV capability layout.
- Validate SR-IOV/MxGPU flows: enable VFs, bind guest drivers, verify VF BAR sizing/addressing, VF counts/stride/offsets, mailbox ack/valid transitions, FLR handling, and per-VF framebuffer allocation visibility.
- Validate IOMMU/SVM behavior where ATS/PRI/PASID are enabled, including DMA isolation and page-request behavior.
- Trigger or observe AER and lane/link events where possible; confirm error status, mask, severity, header log, TLP prefix log, lane error status, and link equalization status decode correctly.
- Confirm no generated register-mask changes alter reserved-bit writes in code paths that use read-modify-write helpers.

## Research Notes

This chunk was read as a generated register definition table rather than hand-written logic. The most important source-tree-aligned conclusion is that the chunk is a hardware contract layer: its correctness is measured by whether AMDGPU and PCIe/virtualization code can address the intended NBIO 7.0 fields without bit corruption. The final merged per-file research should correlate this chunk with the adjacent `nbio_7_0_offset.h` address definitions and with neighboring chunks that contain the start/end of the same endpoint-function blocks.

### subset-b-003085: lines 41513-43979

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 41513-43979

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,118 `#define` field-layout macros and 343 register/address comments for PCIe configuration-space registers under `BIF_CFG_DEV0_EPF1_1`, `BIF_CFG_DEV0_EPF2_1`, `BIF_CFG_DEV0_EPF3_1`, and the beginning of `BIF_CFG_DEV0_EPF4_1`. There are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts in the middle of `BIF_CFG_DEV0_EPF1_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_HVVM_MBOX_DW1`, so the `VF0` through `VF7` shift definitions and the register comment are in the previous chunk while this chunk still includes the later shifts and all masks for the register. It ends in the middle of `BIF_CFG_DEV0_EPF4_1_LINK_STATUS2`, after the `EQUALIZATION_PHASE2_SUCCESS` shift; the remaining `LINK_STATUS2` shifts and all masks continue in the next chunk. The merge lane must reconcile those boundary registers before treating either family as complete.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.0 register interface. For each hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to place or extract the field.
- `<REGISTER>__<FIELD>_MASK`, the encoded mask used to isolate, preserve, clear, or update that field.

This chunk describes the PCIe configuration layout for several endpoint functions exposed through NBIO/BIF. The first section completes part of the `EPF1` GPU-I/O virtualization vendor-specific capability, including host/virtual-machine mailbox handshakes, context and framebuffer accounting fields, per-VF framebuffer allocations, and scheduler data windows. The rest of the chunk moves through repeated PCI-compatible endpoint-function configuration blocks for `EPF2`, `EPF3`, and `EPF4`: standard header fields, BARs, power management, PCI Express capabilities, AER, BAR enhanced capabilities, power budgeting, dynamic power allocation, ACS, ARI, MSI, MSIX, SATA IDP, and selected PCIe link-control/status fields.

## Important Macro Families

The `EPF1` GPU-I/O virtualization section covers:

- `GPUIOV_HVVM_MBOX_DW1` and `GPUIOV_HVVM_MBOX_DW2`, which expose per-VF transmit-acknowledge and receive-valid bits for VFs 0-15 plus PF transmit/receive handshake bits.
- `GPUIOV_CONTEXT`, which defines context size, location, and offset fields for virtualization context storage.
- `GPUIOV_TOTAL_FB` and `GPUIOV_VF0_FB` through `GPUIOV_VF15_FB`, which split each word into framebuffer size and offset fields and expose aggregate available/consumed framebuffer accounting.
- `GPUIOV_OFFSETS`, which points to UVD, VCE, and GFX scheduler windows.
- `GPUIOV_UVDSCH_DW0` through `DW8`, `GPUIOV_VCESCH_DW0` through `DW8`, and `GPUIOV_GFXSCH_DW0` through `DW8`, which are full-width data words for virtualization scheduler payloads.

The `EPF2` and `EPF3` blocks are full repeated PCI endpoint-function configuration layouts:

- Standard PCI header fields: vendor/device IDs, command/status, revision/programming interface/subclass/base class, cache-line/latency/header/BIST, six BARs, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, and adapter IDs.
- Power management capability fields: capability-list headers, capability version, device-specific initialization, auxiliary-current, PME support, PME enable/status, data select/scale, and power state.
- PCI Express capability fields: capability list/header, device capabilities, device control/status, link capabilities/control/status, device/link capability 2, control 2, status 2, slot capability/control/status 2, and feature bits such as payload size, read request size, FLR, relaxed ordering, no-snoop, LTR, OBFF, IDO, ARI forwarding, atomic operations, completion timeout, link speed/width, retraining, ASPM, and equalization status.
- MSI and MSIX fields: MSI control, 32/64-bit message address/data, mask and pending words, MSIX table and pending-bit-array descriptors.
- Vendor-specific and PCIe extended capabilities: vendor capability headers and payload words, Advanced Error Reporting status/mask/severity/log fields, BAR enhanced capability controls for BAR1-BAR6, power-budget data selection and capability fields, DPA capability/control/status/substate allocation fields, ACS capability/control fields, and ARI capability/control fields.

The `EPF4` block begins the same repeated endpoint-function layout, starting at standard PCI identity/header/BAR fields and continuing through power management, PCIe device/link capabilities, and PCIe link status 2. This chunk stops before the rest of `EPF4` link-status2 masks and later MSI/MSIX/extended-capability fields.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not encode register addresses, reset values, access width, read/write permissions, write-one-to-clear behavior, sequencing requirements, firmware ownership, or hardware side effects. Consumers must combine them with sibling generated metadata in `nbio_7_0_offset.h`, `nbio_7_0_default.h`, and `nbio_7_0_smn.h`, then access the registers through AMDGPU helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, or `SOC15_REG_OFFSET` depending on the register aperture.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects a NBIO/BIF PCI configuration register from generated address metadata.
2. The code reads a register value, extracts fields with the `__SHIFT` and `_MASK` constants, or composes a new value while preserving unrelated and reserved bits.
3. The decoded or composed value participates in PCIe device bring-up, SR-IOV/GPU-I/O virtualization setup, doorbell and interrupt routing, power management, link training, error reporting, BAR programming, or capability exposure.

The field names imply several hardware/firmware-managed flows outside the header: PF/VF mailbox handshakes, per-VF framebuffer partitioning, scheduler-table publication for UVD/VCE/GFX virtualization, PCIe power-state transitions, FLR initiation, completion-timeout handling, link retraining/equalization, AER logging, MSI/MSIX interrupt delivery, ACS/ARI routing, DPA substate allocation, and power-budget reporting.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe configuration and vendor-specific registers. Persistence depends on the GPU reset domain, PCIe reset, function-level reset, firmware/BIOS configuration, virtualization manager programming, suspend/resume restore, and explicit AMDGPU writes.

Represented state includes PCI identity and class-code fields, command/status bits, BAR apertures, ROM BAR values, capability-list pointers, power-management state, PCIe device/link capabilities and controls, MSI/MSIX routing state, AER masks/status/logs, BAR capability controls, power-budget and DPA data, ACS and ARI enables, GPUIOV mailbox bits, GPUIOV framebuffer allocations, and scheduler data words. Some fields are status or latched hardware state (`CORR_ERR`, `FATAL_ERR`, `TRANSACTIONS_PEND`, `LINK_TRAINING`, equalization status, AER logs, MSI pending bits), while others are configuration controls that software or firmware may write.

Because many registers are PCI configuration surfaces, values can be visible to the host PCI core, hypervisors, guests, firmware, or user-space diagnostic tooling. Call sites must not infer reset persistence from the mask definitions alone; defaults and reset behavior belong to hardware documentation and sibling generated default/address headers.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must remain synchronized with sibling headers:

- `nbio_7_0_offset.h` provides the matching register offsets.
- `nbio_7_0_default.h` provides generated reset/default values.
- `nbio_7_0_smn.h` provides SMN-indexed NBIO register names used by PCIe/NBIO access paths.
- `nbio_7_0_sh_mask.h` consumers use AMDGPU register helpers to apply these field layouts.

Direct include users in this tree include `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. `nbio_v7_0.c` shows the expected integration pattern: include the default/offset/shift-mask/SMN headers together, then use `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD` around generated symbols. This exact chunk's `EPF1`-`EPF4` symbols are not directly matched by name in those local `.c` files, so they are mostly latent hardware metadata for platform code, firmware interaction, virtualization, PCI config decoding, or future call sites rather than active high-level driver logic in the visible source.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing software to read or write the wrong PCIe configuration bit, leading to broken capability reporting, bad BAR sizing, lost interrupts, AER misreporting, or PCIe link/power-management regressions.
- The chunk starts and ends mid-register. Adjacent chunks are required for complete `GPUIOV_HVVM_MBOX_DW1` and `EPF4_LINK_STATUS2` coverage.
- `EPF2`, `EPF3`, and `EPF4` are mechanically repeated blocks. A generation error in one function can affect only a single virtual or physical endpoint function, which is hard to notice if tests exercise only `EPF0` or `EPF1`.
- GPUIOV mailbox fields are handshake bits. Polling code needs timeouts and must handle missed acknowledgements, stale receive-valid bits, VF index mismatches, and PF/VF ownership races.
- GPUIOV framebuffer size/offset fields are partitioning data. Incorrect masks can expose overlapping VF framebuffer windows or misreport available/consumed memory to virtualization layers.
- PCIe control bits such as FLR, link disable, retrain link, target link speed, completion timeout, no-snoop, relaxed ordering, LTR, OBFF, ARI, ACS, and atomic-operation enables have system-visible effects and may be constrained by firmware, topology, or the host PCI core.
- AER status and log fields may use write-one-to-clear or latch-on-error semantics depending on the hardware register. The mask header does not describe those semantics, so consumers must avoid blind writes.
- Reserved fields are explicitly represented in several registers. Writers should preserve reserved bits unless the hardware specification requires a defined value.

## Test Signals

- Build AMDGPU with NBIO 7.0 and SMU10 paths enabled. Compile-time coverage catches missing or renamed generated symbols used by `nbio_v7_0.c`, `soc15.c`, and power-management include stacks.
- Run generated-header consistency checks: every field with both shift and mask should have a compatible mask position, masks should not overlap unexpectedly within a register, and repeated `EPF2`/`EPF3`/`EPF4` layouts should match except for the endpoint-function number.
- Cross-check this shift/mask chunk against `nbio_7_0_offset.h` and `nbio_7_0_default.h` so every `BIF_CFG_DEV0_EPF*_1_*` field maps to a known register offset and expected default.
- On supported hardware, validate PCI enumeration, BAR sizing, MSI/MSIX interrupt delivery, AER reporting, power-management state transitions, FLR behavior, GPU reset recovery, suspend/resume, and PCIe link retraining/equalization with NBIO 7.0 enabled.
- For virtualization/SR-IOV scenarios, exercise GPUIOV PF/VF mailbox exchange, VF framebuffer allocation reporting, UVD/VCE/GFX scheduler data publication, VF reset handling, and guest-visible PCI capability surfaces.
- For any code that writes these fields, capture register traces before and after changes to confirm reserved bits are preserved, write-one-to-clear fields are handled intentionally, and capability/control fields remain consistent across cold boot, warm reset, and resume.

### subset-b-003086: lines 43980-46461

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 43980-46461

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 shift/mask header. It defines bitfield geometry for PCI/PCIe configuration-space registers in the NBIF/BIF `BIF_CFG_DEV0_EPF*_1` decode namespace. The covered range starts inside endpoint function 4 (`EPF4_1`) at the tail of `LINK_STATUS2`, covers the remainder of the EPF4 capability layout, then covers complete visible endpoint-function blocks for `EPF5_1` and `EPF6_1`, and finally begins `EPF7_1` from standard PCI header fields through `ADAPTER_ID_W`.

The macros do not implement Ceph filesystem behavior despite living under the repository's `ceph-client` source mirror. They are AMD GPU hardware metadata consumed by DRM/AMDGPU code and generated register helpers to encode, decode, or document NBIO PCIe configuration registers.

The chunk contains 2,124 `#define` lines: 1,060 `__SHIFT` macros and 1,064 `_MASK` macros. It also includes three explicit address block comments for `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`, `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp`, and `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`. The source range boundaries are artificial: it begins after the first four `BIF_CFG_DEV0_EPF4_1_LINK_STATUS2` shift definitions and ends before the remaining `BIF_CFG_DEV0_EPF7_1_PMI_*` and later PCIe capability fields.

## Important APIs, Types, and Macros

There are no C functions, structs, enums, or typedefs in this slice. The public interface is a large set of C preprocessor constants following the generated form:

- `BIF_CFG_DEV0_EPF<n>_1_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF<n>_1_<REGISTER>__<FIELD>_MASK`

The `<n>` endpoint-function suffix identifies a PCIe endpoint function image under NBIO device 0. The `_1` qualifier distinguishes this generated config-space view from similarly named `_0` or non-suffixed endpoint and virtual-function views elsewhere in the NBIO headers.

Major covered register families:

- `EPF4_1` tail: `LINK_STATUS2`, reserved slot capability/control/status 2 registers, MSI/MSI-X capability registers, SATA capability and IDP registers, vendor-specific enhanced capability, Advanced Error Reporting (AER), BAR enhanced capability, power budget, Dynamic Power Allocation (DPA), ACS, and ARI.
- `EPF5_1`: standard PCI header fields, PM capability, SATA-specific fields, PCIe capability/device/link capability registers, MSI/MSI-X, vendor-specific capability, AER status/mask/severity/logs, BAR enhanced capability, power budget, DPA, ACS, and ARI.
- `EPF6_1`: the same generated endpoint-function layout shape as `EPF5_1`, including PCI header fields, PM/SATA/PCIe capabilities, interrupt capability registers, AER, BAR power sizing, DPA, ACS, and ARI.
- `EPF7_1` prefix: vendor and device IDs, command/status, revision/class/header/BIST, six base-address registers, adapter/ROM/capability pointer, interrupt line and pin, min/max latency, vendor capability list, and writable adapter ID fields.

Representative field groups and their role:

- Standard PCI command/status masks expose `IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `SERR_EN`, `INT_DIS`, `CAP_LIST`, abort/error status bits, and parity reporting bits.
- Identity/resource masks expose vendor/device IDs, revision/class codes, header type, BAR dwords, subsystem adapter IDs, ROM BAR, capability pointer, and legacy interrupt routing fields.
- PM masks expose PME support, power state, PME enable/status, data select/scale, and bus-power bits.
- PCIe capability masks expose device capability/control/status and link capability/control/status fields, including payload size, read request size, relaxed ordering, no-snoop, link speed/width, active state power management, retrain, clock configuration, and link equalization state.
- MSI/MSI-X masks expose enable bits, vector count encoding, 64-bit addressing support, MSI address/data/mask/pending dwords, MSI-X table size, function mask, enable, table BIR/offset, and PBA BIR/offset.
- AER masks expose uncorrectable status/mask/severity bits for DLP, surprise down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receive overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, AtomicOp egress block, and TLP-prefix block. Correctable error status/mask fields cover receiver errors, bad TLP/DLLP, replay rollover, replay timeout, advisory nonfatal, correctable internal error, and header-log overflow.
- AER log registers expose `TLP_HDR` and `TLP_PREFIX` full-width 32-bit log payloads.
- BAR enhanced capability masks expose BAR size support and BAR index/total/count/size control fields for BAR1 through BAR6.
- Power-budget and DPA masks expose power-budget data selection, base power, scale, PM state/substate, type, rail, DPA substates, latency indicators, DPA status/control, and eight substate power allocation bytes.
- ACS and ARI masks expose peer-to-peer isolation/redirect capability and control bits, source validation, translation blocking, upstream forwarding, egress-control vector size, ARI next-function number, ARI function-group support, and ARI function-group control.
- SATA-specific masks expose `SBRN`, `FLADJ`, `DBESL_DBESLD`, `SATA_CAP_0`, `SATA_CAP_1`, `SATA_IDP_INDEX`, and `SATA_IDP_DATA`, indicating that these endpoint-function templates include SATA/xHCI-style config-space fields alongside generic PCIe fields.

## Control Flow and Runtime Behavior

This header chunk has no runtime control flow. Including it only makes numeric constants available at compile time. Runtime behavior appears when AMDGPU code combines these masks and shifts with register offsets from the companion NBIO 7.0 address headers and with access helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32`, `WREG32`, and `WREG32_FIELD15`.

The typical flow is:

1. Runtime code selects a register address from `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, or an SOC15 register identifier.
2. It reads a 32-bit hardware value from the NBIO or PCIe configuration-space access path.
3. It uses a matching `BIF_CFG_DEV0_EPF*_1_*__SHIFT` and `_MASK` pair to extract a field, or clears and inserts a new field value.
4. If programming hardware, it writes the modified register value back through the AMDGPU register accessor.

The header does not encode sequencing rules. It does not say when to retrain PCIe links, enable MSI/MSI-X, acknowledge AER status, resize BARs, change DPA substates, or enable ACS/ARI. Those policies live in PCI core logic, AMDGPU NBIO code, firmware, platform enumeration, or hardware-specific initialization sequences. This chunk only defines the bit positions those policies rely on.

## State and Persistence

The file itself owns no mutable state, allocates no memory, and persists nothing. The represented state is hardware configuration and status state for NBIO PCIe endpoint-function config images.

Several covered fields are naturally writable configuration state, including PCI command bits, PM status/control, MSI/MSI-X enable and mask fields, BAR control fields, power-budget selection, DPA control, ACS control, and ARI control. Other fields are read-only or status-oriented from a PCIe perspective, such as link status, equalization status, AER status, AER header/TLP-prefix logs, capability IDs, supported sizes, and advertised capability bits. The generated header does not distinguish read-only from writable fields; callers must know the PCIe register semantics and hardware access rules.

Persistence is at the hardware and driver-build level. Reset values are described in `nbio_7_0_default.h`, where matching names such as `smnBIF_CFG_DEV0_EPF4_1_LINK_STATUS2_DEFAULT`, `smnBIF_CFG_DEV0_EPF5_1_*_DEFAULT`, and `smnBIF_CFG_DEV0_EPF6_1_*_DEFAULT` appear. If a mask or shift is wrong, every compiled consumer using that generated macro will continue reading or programming the wrong bits until the header is regenerated and rebuilt.

## Dependencies and Integration Points

This chunk belongs to the NBIO 7.0 generated-register header set:

- `nbio_7_0_sh_mask.h` supplies the field masks and shifts covered here.
- `nbio_7_0_default.h` supplies reset/default values for matching `smnBIF_CFG_DEV0_EPF*_1_*` registers.
- `nbio_7_0_offset.h` and `nbio_7_0_smn.h` supply addressing constants for the broader NBIO 7.0 register set.

Direct in-tree includes of `nbio_7_0_sh_mask.h` include `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. `nbio_v7_0.c` shows the expected integration pattern: it includes `nbio_7_0_default.h`, `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and `nbio_7_0_smn.h`, then uses SOC15 accessors and field macros for NBIO programming. The specific `EPF4_1` through `EPF7_1` config-space masks may be used directly by register dump/debug paths, platform enumeration helpers, virtualization code, or generated diagnostics even when ordinary display or memory-controller paths do not name them explicitly.

The surrounding PCIe subsystem also matters. MSI/MSI-X, PM, AER, ACS, ARI, BAR sizing, and link-state fields must remain consistent with Linux PCI core expectations and with the hardware's advertised capability chain. Capability-list fields such as `CAP_ID`, `NEXT_PTR`, `CAP_VER`, and extended-capability `NEXT_PTR` make these generated definitions part of the config-space topology exposed to software.

## Risks

- Generated-header drift is the primary risk. A single incorrect mask or shift can cause all consumers to extract or write the wrong bits for PCI command, AER, interrupt, BAR, power, or isolation controls.
- The chunk starts and ends mid-register family. The first four `LINK_STATUS2` shifts for `EPF4_1` are outside the assigned range, and `EPF7_1_PMI_STATUS_CNTL` plus later EPF7 capability registers continue after it. Whole-file research must merge neighboring chunks before making complete conclusions.
- Repeated endpoint-function blocks are easy to cross-wire. `BIF_CFG_DEV0_EPF5_1_PCIE_UNCORR_ERR_STATUS` and `BIF_CFG_DEV0_EPF6_1_PCIE_UNCORR_ERR_STATUS` have the same field layout but refer to different config images. Using the wrong endpoint-function prefix would silently target the wrong function's logical register.
- The `_1` namespace must not be conflated with `_0`, non-suffixed, virtual-function, SMN, or `reg`/`cfg` address namespaces in other generated headers. The same semantic register name can exist in several address domains.
- Full-width masks such as BARs, MSI address high dwords, AER header logs, TLP-prefix logs, and vendor scratch registers are mechanically simple but broad. A caller writing through a full-width mask can overwrite an entire hardware-visible dword.
- Reserved fields such as slot capability/control/status 2 are still exposed as masks. Treating reserved masks as writable feature bits could create undefined hardware behavior.
- AER status and mask/severity registers are safety-sensitive for PCIe error reporting. Incorrect masks can hide link errors, misclassify fatal/nonfatal errors, or corrupt diagnostic logs.
- ACS and ARI fields affect device isolation and routing. Incorrectly programming ACS redirect/forwarding bits or ARI function-group bits can affect peer-to-peer routing, IOMMU expectations, and multi-function enumeration.

## Test and Validation Signals

Useful validation is mostly generated-header consistency plus hardware and PCIe enumeration coverage:

- Build AMDGPU users that include `nbio_7_0_sh_mask.h`, especially `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and the SMU10 PowerPlay include path.
- Run a generated-header consistency check that every `BIF_CFG_DEV0_EPF5_1_*` and `BIF_CFG_DEV0_EPF6_1_*` register in this chunk has matching shift/mask pairs and that field names mirror equivalent endpoint-function blocks where expected.
- Cross-check this range against `nbio_7_0_default.h` to confirm matching default entries exist for covered `EPF4_1`, `EPF5_1`, `EPF6_1`, and beginning `EPF7_1` registers.
- Reconcile with neighboring chunks before producing final per-file research: previous chunk contains the start of `EPF4_1_LINK_STATUS2`, and the next chunk contains the rest of `EPF7_1_PMI_STATUS_CNTL` and later EPF7 PCIe capability fields.
- On affected NBIO 7.0 ASICs, validate PCIe enumeration, capability-list traversal, BAR assignment, MSI/MSI-X setup, AER reporting, link training/equalization status, suspend/resume, FLR/reset behavior, and any register dump tooling that decodes `BIF_CFG_DEV0_EPF*_1` fields.
- For virtualization or multi-function scenarios, validate that `EPF5_1`, `EPF6_1`, and `EPF7_1` decode paths remain distinct and that ACS/ARI settings do not break isolation, routing, or function discovery.

### subset-b-003087: lines 46462-48915

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 46462-48915

## Purpose

This chunk is an auto-generated register shift/mask slice for AMD NBIO 7.0 PCI configuration-space fields. It covers the tail of the `BIF_CFG_DEV0_EPF7_1` endpoint/function block, all of the `BIF_CFG_DEV1_EPF0_1` block, and the beginning of `BIF_CFG_DEV1_EPF1_1` through the MSI-X table register. The macros describe bit positions and masks only; they do not execute hardware access themselves.

The definitions are part of the AMDGPU register contract included by `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. Driver code can combine these names with the corresponding address/default headers to read, compose, or decode NBIO PCIe configuration registers without embedding numeric bit constants.

## Public Surface In This Chunk

The public API is a dense set of C preprocessor macros named:

- `BIF_CFG_DEV0_EPF7_1_*__FIELD__SHIFT` and `BIF_CFG_DEV0_EPF7_1_*__FIELD_MASK` for power-management, PCIe capability, interrupt, SATA, vendor-specific, AER, BAR, power-budget, DPA, ACS, and ARI fields.
- `BIF_CFG_DEV1_EPF0_1_*__FIELD__SHIFT` and `BIF_CFG_DEV1_EPF0_1_*__FIELD_MASK` for a full endpoint/function config block, including standard PCI header fields, PCIe capability structures, MSI/MSI-X, SATA IDP, VC resources, AER, secondary PCIe capability lane equalization controls, ACS, LTR, and ARI.
- `BIF_CFG_DEV1_EPF1_1_*__FIELD__SHIFT` and `BIF_CFG_DEV1_EPF1_1_*__FIELD_MASK` for the start of the next endpoint/function block, from vendor/device IDs through MSI-X table fields.

Each register comment, such as `//BIF_CFG_DEV1_EPF0_1_DEVICE_CNTL`, is followed by one or more shift macros and matching mask macros. Single-bit fields use a one-bit mask at the shifted position; multi-bit fields use contiguous masks sized to the PCIe-defined field width. Masks use `L` suffixes because the generated headers are intended for C preprocessor use in 32-bit register expressions.

## Important Register Families

The standard PCI header fields expose vendor/device IDs, command and status control, revision and class-code bytes, cache-line and latency timer bytes, header/BIST fields, six BAR registers, adapter/subsystem IDs, ROM base, capability pointer, interrupt line/pin, and legacy min/max latency fields. The command/status masks include IO, memory, bus-master, special-cycle, memory-write-invalidate, VGA palette snoop, parity, SERR, fast-back-to-back, interrupt-disable, and status bits such as capabilities-list, master data parity, signaled target abort, received target abort, received master abort, signaled system error, detected parity error, and devsel timing.

The PCI power-management group defines capability-list linkage, PM version/support bits, D1/D2 and PME support, current power state, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PM data. For NBIO 7.0 this chunk also includes `SBRN`, `FLADJ`, and `DBESL_DBESLD` fields adjacent to the PM/USB-style capability area.

The PCIe capability group defines PCIe capability list headers, device capabilities/control/status, link capabilities/control/status, and the PCIe 2.0 capability/control/status set. Fields cover payload sizes, read request size, error-reporting enables, relaxed ordering, no-snoop, FLR, completion timeout, ARI forwarding, AtomicOp support, IDO, LTR, OBFF, target link speed, compliance controls, deemphasis, equalization status, negotiated width/speed, data-link active, and link bandwidth status/interrupt enables.

Interrupt capability fields include MSI and MSI-X. MSI macros describe enable, multiple-message capability/enable, 64-bit address support, per-vector masking, low/high message address, data, mask, and pending bits. MSI-X macros describe capability-list linkage, table size, function mask, enable, table BIR/offset, and PBA BIR/offset.

The chunk also defines extended capability families. AER fields cover uncorrectable status/mask/severity bits for DLP, surprise-down, poison, flow-control, completion-timeout, completion-abort, unexpected-completion, receiver-overflow, malformed TLP, ECRC, unsupported-request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, and TLP prefix blocked conditions; correctable status/mask bits cover receiver, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, correctable internal, and header-log overflow. AER capability/control and header/TLP prefix log registers are exposed as full-width fields.

Other PCIe extended groups in the span include vendor-specific capability headers and scratch registers, BAR enhanced capability per BAR1-BAR6, power-budget data select/data/capability, dynamic power allocation capability/status/control and eight substate allocation registers, ACS capability/control, ARI capability/control, LTR max snoop/no-snoop latency fields, virtual-channel port/resource control and status for `DEV1_EPF0`, and secondary PCIe lane equalization control for lanes 0-15.

## Control Flow And State

There is no runtime control flow in this chunk. The effective control flow is compile-time macro substitution:

1. Driver code includes `nbio_7_0_sh_mask.h`.
2. A caller reads a 32-bit NBIO/PCI config register using an address macro from the companion offset header.
3. The caller isolates a field with `value & *_MASK`, then shifts by `*_SHIFT`, or composes a field value by shifting and masking before writing.

The header does not store state. Persistent state lives in the device's NBIO PCI configuration registers, not in the source tree. Some fields represent write-sensitive hardware state, including error status, interrupt enables/masks, FLR initiation, link retraining, target link speed, power-management controls, BAR control, DPA controls, ACS controls, ARI forwarding, and VC resource controls.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header scheme: address macros are in sibling NBIO offset headers, reset values are in `nbio_7_0_default.h`, and these `_sh_mask` macros provide field extraction/composition constants. It also depends on PCI/PCIe architectural semantics for capability list layout, AER, MSI/MSI-X, ACS, ARI, LTR, VC, DPA, and secondary PCIe extended capability encodings.

Integration points are AMDGPU NBIO and SOC initialization paths that include this header, plus PowerPlay/SMU code that needs the same register constants. The actual hardware access path is outside this header and normally goes through AMDGPU register access helpers and PCI config access helpers. Because the macros are globally named and not scoped by a C type, they are shared constants rather than an encapsulated API.

## Risks And Maintenance Notes

- These definitions must stay synchronized with NBIO 7.0 hardware documentation and the matching address/default headers. A correct mask paired with the wrong address macro would silently decode or program the wrong field.
- The chunk is highly repetitive across endpoint/function blocks. Copy-generation drift is a real risk, especially where `DEV0_EPF7`, `DEV1_EPF0`, and `DEV1_EPF1` differ in which extended capabilities are present.
- Some PCIe status fields are write-one-to-clear or otherwise side-effectful at the hardware level. The masks make those fields easy to target, but callers must still follow hardware clearing and ordering rules.
- Link, power, DPA, VC, ACS, ARI, MSI/MSI-X, and AER control fields affect interrupt routing, isolation, error reporting, power state, and PCIe training. Incorrect use can produce device hangs, lost interrupts, bad isolation, or masked fatal errors.
- The macros use fixed 32-bit-style masks with `L` suffixes. Consumers should avoid sign extension or truncation surprises when mixing them with wider arithmetic and should use the established AMDGPU register helper types.
- The source chunk starts in the middle of the `DEV0_EPF7` block and ends in the middle of the `DEV1_EPF1` block, so complete per-function coverage requires adjacent chunks during merge.

## Test Signals

Useful validation signals include:

- Header compile coverage for translation units that include `nbio_7_0_sh_mask.h`, especially `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `smu10_inc.h`.
- Static checks that every `*_SHIFT` in this chunk has a matching `*_MASK`, and that masks are contiguous and aligned with their shift.
- Cross-header checks that registers named here have matching address entries in the NBIO 7.0 offset header and default entries in `nbio_7_0_default.h` where applicable.
- Runtime PCIe capability validation on NBIO 7.0 hardware: decoded link speed/width, payload size, MSI/MSI-X capability state, AER masks/status, ACS/ARI/LTR capability bits, and DPA/VC fields should match lspci/config-space expectations.
- Error-path tests that inject or observe AER status bits and verify the AMDGPU error handling path decodes, masks, and clears the intended fields without disturbing unrelated bits.
- Power-management and link-training tests around D-state changes, PME status, FLR, target link speed, retrain link, equalization status, and DPA substate controls.

### subset-b-003088: lines 48916-51556

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 48916-51556

## Scope

This chunk covers a generated AMD NBIO 7.0 shift/mask header segment. It contains bitfield macros only: no C functions, structs, enums, variables, branches, locks, allocations, or direct MMIO/SMN accesses. The public surface is the generated preprocessor naming convention used by AMDGPU register helpers.

The range starts in the middle of `BIF_CFG_DEV1_EPF1_1`, beginning with the tail of its MSI-X capability and continuing through SATA, PCIe vendor-specific, Advanced Error Reporting, BAR, power-budgeting, Dynamic Power Allocation, ACS, and ARI fields. It then covers the full `nbio_nbif0_bif_cfg_dev1_epf2_bifcfgdecp` register group and begins several MSI-X table-decoder windows:

- `nbio_nbif0_bif_cfg_dev1_epf2_bifcfgdecp`, from `BIF_CFG_DEV1_EPF2_1_VENDOR_ID` through `BIF_CFG_DEV1_EPF2_1_PCIE_ARI_CNTL`.
- `nbio_nbif0_pciemsix_amdgfx_MSIXTDEC`, complete vectors 0 through 31.
- `nbio_nbif0_pciemsix_psp_MSIXTDEC`, complete vectors 0 through 31.
- `nbio_nbif0_pciemsix_usb3_0_MSIXTDEC`, complete vectors 0 through 31.
- `nbio_nbif0_pciemsix_usb3_1_MSIXTDEC`, vectors 0 through 10, ending at `PCIEMSIX_USB3_1_PCIEMSIX_VECT10_CONTROL`.

This source tree is a Ceph/distributed-filesystem mirror, but this header is not Ceph filesystem code. It is imported Linux AMDGPU hardware metadata.

## Purpose

`nbio_7_0_sh_mask.h` defines field shifts and masks for NBIO 7.0 register programming. The generated macros let AMDGPU code use helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, and related SOC15 accessors without open-coding bit positions.

This chunk describes two broad hardware surfaces:

- PCI/PCIe configuration-space fields for a DEV1 endpoint function. These include standard command/status, BAR, MSI/MSI-X, PCIe capability, AER, ACS, ARI, DPA, and power-budget fields.
- MSI-X table entries for AMDGFX, PSP, and USB3 functions. Each vector has low address, high address, message-data, and vector-control fields.

The generated default header has matching defaults for this region. The EPF2 config block defaults are mostly zero, but several PCIe capability fields are nonzero, including `FLADJ` at `0x20`, `PCIE_CAP_LIST` at `0x0000a000`, `PCIE_CAP` at `0x2`, `DEVICE_CAP` at `0x10000000`, `DEVICE_CNTL` at `0x2810`, `LINK_CAP` at `0x00011c03`, `LINK_STATUS` at `0x1`, `LINK_CAP2` at `0x0e`, `LINK_CNTL2` at `0x3`, AER severity/mask defaults, and enhanced capability list pointers. The MSI-X vector-table defaults for AMDGFX, PSP, USB3_0, and USB3_1 are zero in the checked range.

## Important APIs, Types, and Functions

There are no callable APIs or C types in this chunk. The important interface is the macro schema:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit position.
- `<REGISTER>__<FIELD>_MASK` gives the field mask.
- Full-width fields use masks such as `0xFFFFFFFFL`, `0xFFFFL`, or `0xFFL`.
- PCIe MSI-X table address-low fields use `MSG_ADDR_LO__SHIFT == 0x2` and `MSG_ADDR_LO_MASK == 0xFFFFFFFCL`, preserving the 4-byte alignment requirement.
- MSI-X vector control fields expose only `MASK_BIT` at bit 0.

Notable EPF2 field groups include:

- PCI command and status controls: `IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `INT_DIS`, legacy capability status, parity/SERR, and transaction-status flags.
- PCIe device controls: error-reporting enables, relaxed ordering, payload size, extended tags, no-snoop, max read request size, and `INITIATE_FLR`.
- PCIe link capability/status/control fields: speed, width, ASPM/clock power management, link-training state, bandwidth-management bits, negotiated speed/width, and second-generation supported speed controls.
- MSI/MSI-X capability fields: MSI address/data/mask/pending fields plus MSI-X table size, function mask, enable, table BAR indicator, table offset, PBA BAR indicator, and PBA offset.
- AER fields: uncorrectable/correctable status, masks, severities, first-error pointer, ECRC controls, header logs, and TLP prefix logs.
- ACS and ARI fields: source validation, translation blocking, P2P request/completion redirect, upstream forwarding, egress control, direct translated P2P, next-function number, and ARI forwarding.
- BAR capability/control and power-management fields: BAR sizes/indices, power-budget base/data-scale/PM-state/type, DPA capability/status/control, and per-substate power allocations.

The exact runtime accessor path depends on the caller. In `amdgpu/nbio_v7_0.c`, NBIO 7.0 code includes this header and uses adjacent macros for doorbell, interrupt, HDP flush, PCIe indirect index/data, clock-gating, and memory-controller access. This specific chunk is mostly a hardware register-description surface; direct references to the exact EPF2/MSI-X vector macros were not found in AMDGPU C files, which is consistent with many PCI/MSI-X fields being manipulated through generic PCI/MSI mechanisms, firmware, hardware decode, or diagnostics rather than direct ad hoc driver calls.

## Control Flow

The chunk has no local control flow. It participates in external flows:

1. AMDGPU or PCI/firmware code selects a PCI config, MMIO, or SMN register address using the generated offset/config/default headers and the hardware access path for NBIO 7.0.
2. Code reads a register value or prepares a new value.
3. `REG_GET_FIELD` or `REG_SET_FIELD`-style helpers apply the shifts and masks defined here.
4. The caller writes the result back or interprets the extracted value.
5. Hardware consumes the result as PCIe endpoint configuration, AER state, BAR decode control, MSI/MSI-X interrupt-routing state, or a table entry for a specific function.

For MSI-X table entries, the operational flow is normally: program an aligned message address low word, message address high word, and message data for a vector; update or clear the vector `MASK_BIT`; and let device interrupt logic emit the MSI-X write transaction when the vector fires. Pending-bit-array definitions for these MSI-X blocks appear later in the same source file, outside this chunk.

For EPF2 PCIe capabilities, the flow is more PCIe-standard: capability-list pointers expose capability blocks, command and device-control bits gate memory/BM/error behavior, link fields report or control link state, and AER status/mask/severity fields govern error capture and reporting.

## State and Persistence Behavior

This header stores no software state. It names hardware-visible state in the NBIO PCI configuration and MSI-X decode regions.

State represented by the macros is volatile hardware state with reset-domain-specific persistence. Configuration-space values and MSI/MSI-X tables can be reset by GPU reset, PCI function reset, FLR, bus reset, suspend/resume, driver unload/reload, SR-IOV transitions, or firmware reinitialization. Some fields are host-owned after enumeration, while others are hardware-, PSP-, or firmware-owned during boot and reset. The nonzero defaults in `nbio_7_0_default.h` are the generated reset/default model, not necessarily the value observed after firmware and OS enumeration have configured the device.

The MSI-X table windows are especially stateful at runtime: address and data fields hold host interrupt-remapping targets, and the vector `MASK_BIT` gates delivery. Incorrect persistence assumptions can leave interrupts routed to stale APIC/ITS addresses, masked unexpectedly, or delivered while the OS believes a vector is disabled.

Several EPF2 fields have side effects or sticky semantics despite being presented as plain masks. Examples include write-one-to-clear PCIe error status bits, link-control changes, function-level reset initiation, MSI/MSI-X enables/masks, and AER header/TLP log capture. The header does not encode access type, clear-on-write behavior, reset timing, or ownership; consumers must use the PCIe spec, ASIC register database, and driver sequencing.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.0 header set:

- `nbio_7_0_sh_mask.h` supplies the shifts and masks in this chunk.
- `nbio_7_0_default.h` supplies reset/default constants for the same `BIF_CFG_DEV1_EPF2_1_*` and `PCIEMSIX_*` register families.
- `nbio_7_0_offset.h` supplies related PCI configuration offsets. In the checked tree, the visible config-offset names for this EPF2 range are `cfgBIF_CFG_DEV1_EPF2_0_*`, while the shift/mask and default names in this chunk use `BIF_CFG_DEV1_EPF2_1_*` and `smnBIF_CFG_DEV1_EPF2_1_*`; final merged research should verify whether this is a generated function-instance naming convention or an offset/sh-mask/default naming mismatch.
- SOC15 and register-helper macros in AMDGPU consume the `__SHIFT`/`_MASK` convention.

Runtime integration points include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, which includes this header and provides the NBIO 7.0 function table for AMDGPU.
- Generic Linux PCI configuration and MSI/MSI-X infrastructure, which owns much of the semantic behavior for command/status, BARs, MSI, MSI-X, AER, ACS, ARI, and DPA fields.
- PSP and USB3 functional blocks represented by dedicated MSI-X decode windows.
- AMDGFX interrupt handling, where the programmed MSI-X message address/data eventually routes hardware interrupts to the host.
- Firmware/BIOS/PSP initialization paths that may prepopulate or protect parts of PCIe configuration and interrupt state before AMDGPU probes.

## Risks and Edge Cases

- The chunk begins after the `BIF_CFG_DEV1_EPF1_1_MSIX_TABLE` comment and includes only that register's mask line followed by `MSIX_PBA` and later fields. The previous chunk is required for a complete EPF1 MSI-X table definition.
- The chunk ends at `PCIEMSIX_USB3_1_PCIEMSIX_VECT10_CONTROL`; the rest of USB3_1 vectors and the MSI-X PBA definitions continue later in the file. Final file-level research must stitch the table boundary.
- Offset/header alignment needs care because `nbio_7_0_offset.h` visibly uses `cfgBIF_CFG_DEV1_EPF2_0_*` for the matching PCI config offsets, while this chunk uses EPF2 `_1` names in shift/mask/default macros.
- PCIe status and AER fields may be sticky or write-one-to-clear. Treating masks as normal read/write storage can drop error evidence or fail to clear latched conditions.
- MSI-X address-low fields intentionally mask off bits 1:0. A generator bug or manual change here can create misaligned interrupt message writes.
- Programming `MASK_BIT`, function-mask, or MSI-X enable fields in the wrong order can lose interrupts or deliver them to stale vectors.
- `INITIATE_FLR`, link-control, ACS, ARI, and BAR-control fields can change device topology, DMA reachability, or reset behavior. Direct driver writes should be limited to documented sequences.
- The vector tables are split by function (`AMDGFX`, `PSP`, `USB3_0`, `USB3_1`). Cross-programming a vector table with the wrong function prefix can compile cleanly because the field shapes are identical.
- Many fields are PCI-standard but the generated header does not mark reserved bits. Read-modify-write paths must preserve reserved and hardware-owned bits unless the ASIC programming guide says otherwise.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.0, especially the `nbio_v7_0.c` include path, to catch missing or renamed macros.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: every register in this line range should have the expected `__SHIFT`/`_MASK` pairs, matching defaults, and correct function-instance naming.
- Validate chunk-boundary continuity: EPF1 MSI-X table fields start in the previous chunk, and USB3_1 vectors continue after vector 10 in the next chunk.
- Verify that all MSI-X vector table entries follow the repeated four-register pattern: `ADDR_LO` shift 2/mask `0xFFFFFFFC`, `ADDR_HI` full 32-bit mask, `MSG_DATA` full 32-bit mask, and `CONTROL.MASK_BIT` bit 0.
- On NBIO 7.0 hardware, validate interrupt delivery for AMDGFX, PSP, and USB3 MSI-X vectors after probe, reset, suspend/resume, and MSI/MSI-X reconfiguration.
- Exercise PCIe link and error paths: AER status/mask/severity reporting, correctable and uncorrectable error capture, FLR behavior, link speed/width reporting, and capability-list enumeration.
- Compare runtime PCI config-space dumps with generated defaults only at the correct phase. Post-enumeration values are expected to differ from reset defaults because the OS, firmware, and device initialization write command, BAR, MSI/MSI-X, and AER fields.
- For any generated-header change, include semantic checks for address alignment, reserved-bit preservation, and field-name-to-register-family mapping, not just compile coverage.

## Unresolved Cross-Chunk References

The previous chunk contains the beginning of the `BIF_CFG_DEV1_EPF1_1_MSIX_TABLE` definition. The next chunk continues `PCIEMSIX_USB3_1` beyond vector 10 and later reaches the MSI-X pending-bit-array registers for the same function families. The final per-file document should merge those boundaries before claiming complete MSI-X table/PBA coverage.

### subset-b-003089: lines 51557-54232

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

### subset-b-003090: lines 54233-56614

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 54233-56614

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,382 source lines in the requested range, including 1,100 `__SHIFT` constants, 1,082 `_MASK` constants, and 198 register comment markers. There are no C functions, structs, enums, storage declarations, locks, allocations, or executable statements here.

The range starts at the tail of `BIFPLR0_1_PCIE_L1_PM_SUB_CAP`, where only the final mask definitions are present because the shift definitions and first masks are in the previous chunk. It then completes the `BIFPLR0_1` L1 PM Substates, Downstream Port Containment, Root Port PIO error logging, and Enhanced Speed Mode capability register layouts. The range then enters `addressBlock: nbio_pcie0_bifplr1_cfgdecp` and covers most of the `BIFPLR1_1` PCI/PCIe bridge configuration space: classic PCI config fields, PCIe capability, MSI and subsystem IDs, vendor-specific and VC capabilities, AER, secondary PCIe capability, per-lane equalization controls for lanes 0-15, ACS, multicast, L1 PM Substates, DPC, Root Port PIO logging, and ESM capability registers through the middle of `BIFPLR1_1_PCIE_ESM_CAP_6`. The next chunk is required for the remaining `ESM_CAP_6` masks and later `BIFPLR1_1` registers.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 hardware register interface. Each hardware field is represented by:

- `<REGISTER>__<FIELD>__SHIFT`, the least significant bit position of the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate or update the field.

Runtime AMDGPU code combines these constants with addresses from `nbio_7_0_offset.h`/`nbio_7_0_smn.h`, defaults from `nbio_7_0_default.h`, and register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, and `WREG32_PCIE`. This range does not implement PCIe policy itself; it defines the software-visible bit layout needed by NBIO 7.0 bridge, PCIe link, error-reporting, isolation, multicast, and power-management paths.

## Important Macro Families

The `BIFPLR0_1` tail provides the second half of one PCIe root-port block:

- `BIFPLR0_1_PCIE_L1_PM_SUB_*` defines L1 PM Substates capability/control fields: L1.1/L1.2 support and enables, ASPM and PCI-PM enable bits, common-mode restore time, LTR L1.2 threshold value/scale, and T_POWER_ON scale/value.
- `BIFPLR0_1_PCIE_DPC_*` defines Downstream Port Containment enhanced capability headers, DPC trigger enables, completion/interrupt controls, software trigger, corrected-error enable, poison-egress blocking, trigger status/reason, root-port busy, first-error pointer, and DPC error source ID.
- `BIFPLR0_1_PCIE_RP_PIO_*` defines Root Port PIO status/mask/severity/sys-error/exception bits for configuration, I/O, and memory unsupported-request completions, completer aborts, and completion timeouts, plus TLP header logs, implementation-specific log, and prefix logs.
- `BIFPLR0_1_PCIE_ESM_*` defines Enhanced Speed Mode capability list/header/status/control and ESM capability bitmaps. The ESM bitmaps map one bit per tenth-GT/s bucket, from `ESM_2P5G` through the `ESM_CAP_7` region starting at `ESM_25P0G` and later values outside this chunk.

The `BIFPLR1_1` address block begins a repeated NBIO PCIe bridge/function register map:

- Standard PCI bridge config registers include vendor/device ID, command/status, revision/interface/class, cache/latency/header/BIST, secondary/subordinate bus numbers, I/O and memory windows, prefetchable base/limit upper halves, interrupt line/pin, bridge control, and extended bridge control.
- Power management and PCIe capability registers include PMI capability/status/control, PCIe capability flags, device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, and the PCIe 2.0 capability/control/status extensions.
- MSI and identity-related registers include MSI capability list/message control, message address/data fields, subsystem ID capability, MSI map capability/address, and vendor-specific enhanced capability headers.
- Virtual Channel registers define port VC capability/control/status and VC0/VC1 resource capability/control/status fields, including traffic-class maps, arbitration select/table offsets, load controls, and negotiation-pending status.
- AER registers define uncorrectable error status/mask/severity bits, correctable error status/mask bits, AER capability/control, header logs, root error command/status, error source IDs, and TLP prefix logs.
- Secondary PCIe capability registers define link control 3, lane error status, and per-lane equalization controls for lanes 0-15. Each lane equalization register provides downstream TX preset, downstream RX preset hint, upstream TX preset, and upstream RX preset hint fields.
- ACS registers define access-control capability and enable bits: source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, peer-to-peer egress control, direct translated peer-to-peer, and egress vector size.
- Multicast registers define multicast capability/control, MC base address words, receive vectors, block-all vectors, untranslated blocking vectors, and overlay BAR sizing/base fields.
- The second `BIFPLR1_1_PCIE_L1_PM_SUB_*`, `DPC_*`, `RP_PIO_*`, and `ESM_*` families mirror the `BIFPLR0_1` definitions for this bridge/function instance.

## APIs, Types, And Functions

There are no callable APIs or local C types in this source range. The API surface is the generated preprocessor namespace. Consumers depend on exact spelling and value consistency among register names, field names, shifts, masks, offsets, SMN names, and defaults.

The constants are untyped integer macros. The mask literals use an `L` suffix and cover 8-bit, 16-bit, and 32-bit config-space fields depending on the register. They describe bit placement only. They do not encode access permissions, side effects, write-one-to-clear behavior, sticky/latch behavior, polling rules, firmware ownership, reset domains, ordering requirements, or whether a field is implemented on a given ASIC/package. Those semantics must come from the hardware register database and the code path using the field.

## Control Flow

This header segment has no local control flow. Runtime flow is external:

1. AMDGPU code selects the NBIO 7.0 register address from the generated offset or SMN header.
2. It reads a register, decodes fields with these `__SHIFT`/`_MASK` constants, or composes a new register value with field helper macros.
3. The driver writes the result back, polls a status bit, forwards decoded status to error handling, or uses it in PCIe link/power-management policy.

Likely runtime flows touching this region include PCIe bridge enumeration support, bus-master/memory/interrupt enable handling, PCIe capability discovery, link capability reporting, link status diagnostics, ASPM/L1.1/L1.2 programming, MSI setup, AER error collection, DPC containment handling, ACS isolation policy, virtual-channel and multicast capability exposure, PCIe Gen3+ equalization diagnostics, and ESM capability reporting.

## State And Persistence Behavior

The header stores no state. It names hardware-visible state in NBIO 7.0 PCIe configuration and extended capability registers. Persistence is governed by PCIe config-space reset rules, NBIO reset domains, ASIC reset, firmware/BIOS initialization, Linux PCI core configuration, AMDGPU initialization, runtime power management, suspend/resume restore, GPU reset, and SR-IOV PF/VF ownership.

Represented state includes command enables, bridge window configuration, interrupt routing, PM status/control, device/link/slot/root capability and status, MSI address/data programming, VC negotiation and resource controls, AER masks/severity/status/logs, root error reporting, lane equalization presets and hints, ACS controls, multicast vectors and overlay BAR fields, L1 Substate timing/control, DPC control/status/source, Root Port PIO error classifications and logs, and ESM supported-speed bitmaps.

Many status and error fields are not ordinary persistent storage. AER, Root Port PIO, DPC, lane error, link status, and root error status fields may be sticky, write-one-to-clear, hardware-updated, or interrupt-coupled depending on the underlying register semantics. Command/control fields such as bus mastering, memory access, ASPM/L1 Substates, DPC trigger/interrupt enable, ACS redirect, multicast enable, and bridge windows can affect live traffic and isolation.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.0 register database and must stay aligned with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h` for matching config/SMN register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h` for SMN-addressed register names used by PCIE/NBIO access helpers.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h` for reset/default values. The companion defaults include the same `smnBIFPLR0_1` and `smnBIFPLR1_1` register families, including L1 PM Substates, DPC, RP PIO, ESM, PCIe capability, AER, lane equalization, ACS, and multicast defaults.

Direct include users in this source tree are `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Display resource files include the NBIO 7.0 offset header for address-level integration. The functional NBIO 7.0 code around these includes manages revision detection, memory-controller access, doorbell ranges, HDP remaps, clock gating, interrupt handling, GPU virtualization, and PCIe/NBIO register access; this chunk supplies part of the bitfield vocabulary for that broader surface.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing wrong PCIe config-space decoding or programming. The highest-risk fields in this chunk are bridge command/window bits, AER status/mask/severity, DPC control/status, ACS controls, L1 Substate enables/timing, lane equalization fields, multicast vectors, and error log fields.
- The range begins and ends mid-register-family. `BIFPLR0_1_PCIE_L1_PM_SUB_CAP` is incomplete without the previous chunk, and `BIFPLR1_1_PCIE_ESM_CAP_6` is incomplete without the next chunk.
- The `BIFPLR0_1` and `BIFPLR1_1` families are repetitive by design. A difference in prefix may simply identify another bridge/function instance, while a mismatched mask width or shift can indicate register-database or generator drift.
- Some PCIe status and error fields may be write-one-to-clear, latched, or hardware-updated. Blind read-modify-write sequences can accidentally clear events, preserve stale error bits, or change interrupt behavior.
- ACS, multicast, bridge window, and command-register fields affect DMA reachability, peer-to-peer routing, memory/I/O forwarding, and isolation. Incorrect values can create functional failures or security/isolation regressions.
- L1 PM Substates and link/equalization controls affect live PCIe link behavior. Bad settings can produce link training failures, retrains, poor resume behavior, timeouts, or AER storms.
- DPC and Root Port PIO fields are tied to containment and error reporting. Incorrect masks or enables can hide endpoint failures, over-report benign errors, or leave a device contained unexpectedly.
- ESM capability bitmaps encode advertised speed support. A one-bit shift error can misreport supported link speeds to later policy code or diagnostics.

## Test Signals

- Build AMDGPU with SOC15/NBIO 7.0 and SMU10 support enabled. Direct macro users catch missing or renamed generated symbols.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: offset/default/shift/mask name alignment, mask-width checks, field non-overlap checks, and repeated-instance comparisons between `BIFPLR0_1` and `BIFPLR1_1`.
- Validate chunk boundaries during merge: `BIFPLR0_1_PCIE_L1_PM_SUB_CAP` should be complete when the previous chunk is present, and `BIFPLR1_1_PCIE_ESM_CAP_6` should continue with the remaining shifts/masks in the next chunk.
- On NBIO 7.0 hardware, boot and enumerate PCIe devices while checking negotiated link width/speed, link status, AER counters, DPC status, and absence of unexpected PCIe error logs.
- Exercise suspend/resume, runtime power management, GPU reset, and link retraining paths with ASPM/L1.1/L1.2 enabled and disabled to catch L1 Substate field regressions.
- Run PCIe error-injection or fault tests where available to confirm AER, Root Port PIO, DPC status/source/log fields decode as expected.
- Validate ACS/IOMMU isolation and peer-to-peer DMA behavior on platforms where ACS policy matters.
- Use lane equalization diagnostics on high-speed links to check per-lane preset/hint decoding for lanes 0-15.
- Compare visible defaults against `nbio_7_0_default.h` and hardware reset reads for representative registers such as L1 PM Substate controls, AER masks/severity, lane equalization defaults, RP PIO masks, and ESM capability bitmaps.

### subset-b-003091: lines 56615-59014

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 56615-59014

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,181 `#define` field-layout macros and 215 register-family comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the tail of `BIFPLR1_1_PCIE_ESM_CAP_6`, completes `BIFPLR1_1_PCIE_ESM_CAP_7`, covers the `nbio_pcie0_bifplr2_cfgdecp` address block from `BIFPLR2_1_VENDOR_ID` through `BIFPLR2_1_PCIE_ESM_CAP_7`, and then begins the `nbio_pcie0_bifplr3_cfgdecp` address block through the first field masks of `BIFPLR3_1_DEVICE_CAP2`. Adjacent chunks are required for the complete `BIFPLR1_1_PCIE_ESM_CAP_6` and `BIFPLR3_1_DEVICE_CAP2` register views.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.0 register interface. Each visible register field exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, preserve, clear, or update the field.

This chunk maps PCIe bridge/root-port configuration-space fields for the `BIFPLR2_1` instance and the start of the same layout for `BIFPLR3_1`. The constants describe standard PCI/PCIe bridge identity, command/status, bus-number, BAR/window, interrupt, power-management, PCIe capability, slot/root/device/link, MSI, subsystem ID, virtual channel, device serial number, AER, secondary PCIe, equalization, ACS, multicast, L1 PM substate, DPC, root-port PIO, and ESM capability registers. Although this repository path is under a `ceph-client` source mirror, this header segment is AMDGPU hardware metadata and has no direct distributed-filesystem behavior.

## Important Macro Families

The opening `BIFPLR1_1_PCIE_ESM_CAP_*` tail completes ESM capability bitmap definitions for advertised equalization/speed-mode points. `PCIE_ESM_CAP_6` maps `ESM_22P0G` through `ESM_24P9G` masks, and `PCIE_ESM_CAP_7` maps `ESM_25P0G` through `ESM_28P0G` shifts and masks.

The `BIFPLR2_1` base PCI bridge configuration fields cover identity and bridge setup: vendor/device ID, command and status bits, revision/class/prog-interface bytes, cache-line and latency timer, header/BIST, primary/secondary/subordinate bus numbers, secondary latency, IO/memory/prefetchable bridge windows, upper prefetchable window halves, high IO base/limit, capability pointer, interrupt line/pin, bridge control, and extended bridge control.

The `BIFPLR2_1` power-management and PCIe capability fields describe capability-list headers, PCI PM version/PME/D-state support, PM status/control, PCIe capability type/version/slot/interrupt identity, device capabilities/control/status, link capabilities/control/status, slot capabilities/control/status, root control/capability/status, and PCIe 2.0+ device/link/slot capability/control/status registers.

The MSI and platform identity area provides MSI capability list/control/address/data fields, 64-bit MSI data, subsystem vendor/device IDs, and MSI mapping capability/address registers. Vendor-specific enhanced capability headers, two scratch registers, and capability-list links are also defined.

The virtual-channel area defines VC enhanced capability headers, port VC capability/control/status, and VC0/VC1 resource capability/control/status. These fields include traffic-class to VC mapping, port arbitration table load/select/status, VC ID, VC enable, max time slots, and negotiation-pending indicators.

The AER and secondary PCIe areas are large: uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header and TLP prefix logs, root error command/status/source ID, secondary PCIe capability, link control 3, aggregate lane error status, and per-lane equalization controls for lanes 0 through 15. The lane equalization registers repeat the same downstream/upstream TX preset and RX preset-hint field layout for every lane.

The access/isolation and advanced feature area covers ACS capability/control bits, multicast capability/control/address/receive/block/overlay BAR fields, L1 PM substate capability/control/timing fields, DPC capability/control/status/error-source fields, root-port PIO status/mask/severity/system-error/exception fields, and PIO header/implementation-specific/prefix logs.

The `BIFPLR2_1_PCIE_ESM_*` block defines ESM enhanced capability metadata, header/status/control registers, and capability bitmaps from `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`. These bitmaps advertise support points from `ESM_0P0G` up through `ESM_28P0G`.

The closing `BIFPLR3_1` section begins a second PCIe bridge/root-port decode block. It mirrors the early `BIFPLR2_1` base, power-management, and PCIe capability layout: identity, command/status, bus windows, interrupt/bridge control, PM capability/control, PCIe device/link/slot/root controls and status, and starts `DEVICE_CAP2` before the chunk ends.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not provide register addresses, reset values, access width, access permissions, write-one-to-clear behavior, side-effect semantics, or sequencing requirements. Consumers must combine them with companion NBIO 7.0 address/default headers and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, PCI config helpers, or NBIO/SMN accessors appropriate for the target register.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU or PCIe-related code selects a `BIFPLR*_1_*` register address from sibling generated metadata.
2. The code reads a PCIe/NBIO register and decodes fields with these `__SHIFT` and `_MASK` constants, or composes a new register value while preserving unrelated and reserved bits.
3. The decoded or written values influence PCIe bridge enumeration, link training, root-port power management, MSI routing, AER/DPC error handling, access-control policy, virtual-channel setup, L1 PM substates, lane equalization, and ESM capability handling.

The chunk implies several asynchronous hardware/protocol flows outside the header: capability-list walking, PME signaling, link retraining and equalization, AER status capture and masking, DPC containment, VC negotiation, ACS isolation enforcement, L1 substate entry/exit timing, MSI delivery, and root-port PIO error logging.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible configuration and status state in NBIO PCIe bridge/root-port registers. Persistence depends on GPU reset domains, PCIe hot/warm reset, firmware/BIOS initialization, suspend/resume restore, runtime power management, and explicit AMDGPU or PCI core writes.

Represented state includes identity readbacks, configuration enables, bridge windows, bus numbering, error-status latches, error masks and severities, PME/D-state state, link speed/width/training state, equalization status and presets, MSI addresses/data, VC and ACS policy state, L1 PM substate timing and enables, DPC trigger/status/source state, root-port PIO logs, and ESM capability/control/status bitmaps. Some fields are capability/read-only indicators, some are live status or latched error bits, and some are writable policy/control fields. The mask definitions alone do not distinguish those access classes.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must remain synchronized with sibling generated headers, especially NBIO 7.0 offset/address/default metadata. Include users normally reach these macros through AMDGPU ASIC register include stacks rather than including the chunk directly.

Important integration points include AMDGPU NBIO initialization, PCIe bridge/root-port setup, GPU reset and resume restore paths, PCIe link training/recovery, AER and DPC handling, MSI configuration, virtual-channel programming, access-control/peer-to-peer isolation, L1 power-management policy, and diagnostics that inspect lane equalization or ESM capability state. The Linux PCI core may own many standard PCI/PCIe config fields conceptually, while AMDGPU accesses NBIO-specific instances and hardware-generated mirrors through SOC15/NBIO access paths.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing the driver to decode or write the wrong PCIe bridge bit, which may appear as enumeration failures, broken BAR/window routing, bad interrupt/MSI setup, incorrect error reporting, or unstable link recovery.
- The chunk boundaries split two register families: `BIFPLR1_1_PCIE_ESM_CAP_6` starts before this range, and `BIFPLR3_1_DEVICE_CAP2` continues after it. Whole-file research must reconcile adjacent chunks before treating those registers as complete.
- Many status and error registers are likely latched or write-one-to-clear in hardware, but that behavior is not encoded in these macros. Call sites need the hardware spec or access helpers to avoid losing diagnostics or clearing errors accidentally.
- Bridge window and bus-number masks affect address routing. Incorrect field use can route MMIO/IO transactions to the wrong downstream range or block valid traffic.
- Link control, equalization, and L1 PM substate fields are timing and signal-integrity sensitive. Bad values can degrade performance or produce intermittent link failures rather than immediate software errors.
- ACS, VC, multicast, and DPC fields affect isolation, peer-to-peer routing, traffic-class mapping, and containment. Misprogramming can create security/isolation holes or overly aggressive error containment.
- Repeated `BIFPLR2_1_PCIE_LANE_N_EQUALIZATION_CNTL` definitions are mechanically similar across lanes 0-15, so a generator or copy error may affect only one lane and be hard to detect without per-lane validation.
- Reserved fields are explicitly present in several registers. Writers must preserve reserved bits unless hardware documentation explicitly permits a value.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing, renamed, or malformed generated symbols used by consumers.
- Run generated-header consistency checks: every field should have a compatible `__SHIFT`/`_MASK` pair, masks within a register should not overlap unexpectedly, and repeated lane-equalization definitions should match across lanes except for lane number.
- Cross-check this header against sibling NBIO 7.0 address/default headers so each `BIFPLR1_1`, `BIFPLR2_1`, and `BIFPLR3_1` field maps to a known register and reset/default definition.
- On supported hardware, validate PCIe enumeration, bridge window programming, BAR reachability, MSI delivery, link speed/width negotiation, link retraining, suspend/resume, hot/warm reset, and GPU reset recovery.
- Exercise AER/DPC paths by checking correct decoding of uncorrectable/correctable/root error status, masks, severities, source IDs, header logs, TLP prefix logs, and root-port PIO logs.
- Validate power-management behavior around PM D-states, PME, ASPM/L1 substates, common-mode restore time, LTR thresholds, and T-power-on timing.
- Inspect lane equalization and ESM readbacks during Gen3+ link training to ensure decoded presets, phase status, lane error state, and advertised speed-mode capability bits match hardware expectations.

### subset-b-003092: lines 59015-61422

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 59015-61422

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,169 `#define` field-layout macros and 237 register-family comments across 2,408 source lines. There are no C functions, structs, enums, global variables, allocations, locks, or executable statements in this range.

The range starts in the middle of `BIFPLR3_1_DEVICE_CAP2`, after the `CPL_TIMEOUT_RANGE_SUPPORTED` shift and mask definitions from the previous chunk, and continues through the rest of the `BIFPLR3_1` PCIe root-port/configuration template. It then switches at `addressBlock: nbio_pcie0_bifplr4_cfgdecp` to the parallel `BIFPLR4_1` template, covering its conventional PCI bridge header, PCI PM/PCIe capability, MSI, SSID, MSI mapping, vendor-specific, virtual-channel, device-serial-number, Advanced Error Reporting, secondary PCIe capability, and per-lane equalization definitions through lane 7. The source boundary ends before `BIFPLR4_1_PCIE_LANE_8_EQUALIZATION_CNTL` and later lane definitions.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMD's generated NBIO 7.0 register interface. For each hardware register or PCI configuration-space word it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit index used to position or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the encoded mask used to isolate, preserve, clear, or update that field.

This chunk describes software-visible PCIe bridge/root-port configuration for `BIFPLR3_1` and `BIFPLR4_1`. The represented fields cover PCIe device/link capability and control words, MSI programming, subsystem identity, MSI mapping windows, vendor-specific capability headers, Virtual Channel resources, Device Serial Number, Advanced Error Reporting, secondary PCIe equalization controls, Access Control Services, multicast routing/filtering, L1 PM substates, Downstream Port Containment, Root Port PIO error reporting, and ESM capability/status/control data.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem behavior.

## Important Macro Families

The `BIFPLR3_1` continuation starts at PCIe Capability 2 and then covers extended root-port capabilities:

- Device/link capability 2 and control 2 fields expose completion-timeout support/control, ARI forwarding, AtomicOp routing/completion support, ID-based ordering, LTR, OBFF, end-to-end TLP prefix support/blocking, target link speed, compliance entry, autonomous speed disable, de-emphasis, equalization status, and link equalization request status.
- MSI and subsystem identity fields describe capability-list links, MSI enable/multiple-message state, 64-bit MSI support, per-vector masking support, MSI address/data payloads, subsystem vendor/device identifiers, and MSI-map enable/fixed/type/base-address fields.
- Vendor-specific capability fields define PCIe VSEC metadata, VSEC ID/revision/length, and scratch words.
- Virtual Channel fields define capability-list metadata, port VC capability and arbitration-table controls, VC arbitration-table load/status, VC0/VC1 resource capabilities, traffic-class-to-VC mapping, VC IDs, enable bits, and negotiation-pending status.
- Device Serial Number fields expose enhanced-capability metadata and the low/high serial-number dwords.
- Advanced Error Reporting fields define uncorrectable error status/mask/severity bits, correctable error status/mask bits, ECRC generation/check capability and enablement, first-error pointer, multiple-header receive controls, TLP-prefix-log presence, header logs, root error command/status, error source IDs, and TLP prefix logs.
- Secondary PCIe fields define link-control-3 equalization trigger and interrupt enablement, lower SKP OS generation enablement, lane error bitmap, and lane 0 through lane 15 equalization controls with downstream/upstream TX presets and RX preset hints.
- ACS fields cover source validation, translation blocking, peer-to-peer request/completion redirection, upstream forwarding, egress control, direct translated P2P, I/O request blocking, memory target access, and unclaimed-request redirect controls.
- Multicast fields define multicast capability/control, MC address dwords, receive masks, block-all masks, untranslated-block masks, and overlay BAR values.
- L1 PM Substates fields define ASPM/PCI-PM L1.1 and L1.2 support/enables, common-mode restore time, power-on value/scale, T-power-on programming, and clock power-management capability.
- DPC and Root Port PIO fields define DPC capability/control/status, trigger reason/detail, interrupt/message numbers, containment state, error source IDs, PIO status/mask/severity/system-error/exception fields, and PIO header/prefix/impspec logs.
- ESM fields define enhanced capability metadata, ESM header dwords, status/control bits, and capability dwords 1 through 7.

The `BIFPLR4_1` portion repeats the same root-port/bridge configuration pattern from its start through lane 7 equalization:

- Conventional PCI bridge header fields include vendor/device ID, command/status, revision/class codes, cache-line/latency/header/BIST values, secondary/subordinate bus numbers, I/O and memory base/limit windows, prefetchable window upper dwords, capability pointer, interrupt line/pin, IRQ bridge control, and extended bridge control.
- PCI command/status fields describe I/O and memory access enables, bus mastering, parity/SERR response, interrupt disable/status, capability-list presence, DEVSEL timing, target/master abort reporting, and detected parity error.
- PCI PM and PCIe base capability fields describe PM capability metadata, D-state/PME support and state, PCIe device/port type, slot implementation, device/link/slot/root capabilities, controls, and status.
- MSI, SSID, MSI-map, VSEC, Virtual Channel, Device Serial Number, AER, root error, secondary PCIe, link-control-3, lane error, and lane 0 through lane 7 equalization definitions mirror the `BIFPLR3_1` field families above.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. Consumers include the header and combine these shifts/masks with register addresses/defaults from sibling generated NBIO 7.0 headers.

The constants are untyped preprocessor integer literals, generally with an `L` suffix for masks. They encode only field geometry. They do not encode register address, reset value, access width, read/write permission, write-one-to-clear behavior, privilege requirements, ordering constraints, firmware ownership, or side effects. Callers must get those semantics from the hardware specification, companion generated headers, and the AMDGPU register-access path.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects an NBIO/PCIe register or configuration-space offset from a companion generated address header.
2. The code reads a hardware value, extracts fields with `__SHIFT` and `_MASK` constants, or composes an updated value while preserving unrelated and reserved bits.
3. The decoded value drives PCIe probing, bridge/window setup, interrupt setup, link management, power-management policy, virtualization/isolation policy, error reporting, or diagnostics; composed values program hardware controls.

Fields in this chunk participate in flows such as PCI bridge enumeration, memory and I/O window decode, bus-mastering enablement, MSI programming, PCIe link retraining and equalization checks, LTR/OBFF and L1-substate power management, AER collection/masking/clearing, DPC containment and recovery, ACS isolation, multicast filtering, VC arbitration/resource negotiation, root-port PIO diagnostics, and ESM status/control handling.

## State And Persistence Behavior

The header itself owns no mutable state and persists nothing. It describes hardware-visible state in NBIO PCIe root-port/bridge registers. Persistence is determined by the GPU/NBIO reset domain, PCIe hot/warm/cold reset, link reset, function-level reset where applicable, suspend/resume save-restore, firmware or BIOS programming, hypervisor/PF policy, and explicit AMDGPU writes.

Represented state includes PCI identity/class values, command/status bits, bus-number and aperture windows, interrupt routing fields, PM state and PME indicators, PCIe device/link/slot/root controls and statuses, MSI address/data state, virtual-channel mappings and negotiation status, serial-number dwords, AER status/mask/severity/logs, root error command/status, link equalization presets/status, ACS and multicast policy, L1-substate timing/enables, DPC trigger/status/interrupt state, root-port PIO error logs, and ESM status/control/capability data.

Some fields are static capabilities, some are writable policy, some are live status, and some are sticky or side-effecting command/status bits. Examples include `MEM_ACCESS_EN` and `BUS_MASTER_EN` gating decode/DMA, link retrain/equalization command bits affecting live PCIe link state, MSI enables affecting interrupt delivery, AER/DPC/PIO status and log registers preserving diagnostic evidence, and ACS/multicast/VC fields affecting routing and isolation. The generated masks alone are insufficient to infer persistence or clear semantics.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must remain synchronized with sibling headers:

- `nbio_7_0_default.h` provides matching reset/default values such as `smnBIFPLR3_1_*_DEFAULT` and `smnBIFPLR4_1_*_DEFAULT`.
- `nbio_7_0_offset.h` and `nbio_7_0_smn.h` provide address metadata for the same NBIO generation where present.
- AMDGPU helper macros such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, and NBIO/SMN/PCIe configuration access helpers consume these field constants.

Direct include users in this source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Higher-level integration is through AMDGPU PCIe/NBIO initialization, GPU reset, interrupt setup, power management, virtualization/isolation, link/error handling, and hardware diagnostics.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while making software read, preserve, clear, or write the wrong hardware bit. This is especially risky for command, bridge-window, interrupt, link-control, AER, DPC, ACS, VC, and power-management fields.
- The chunk starts and ends mid-family. The previous chunk is required for the complete `BIFPLR3_1_DEVICE_CAP2` definition, and the next chunk is required for the rest of `BIFPLR4_1` lane equalization and any following extended capabilities.
- Many PCIe status fields are sticky or write-one-to-clear in hardware even though this header only names masks. Treating them as ordinary writable state can lose error evidence or fail to clear a condition.
- Bridge command and aperture fields gate MMIO/I/O decode and bus mastering. Incorrect masks can break PCI probing, expose the wrong address window, or enable DMA at the wrong time.
- MSI address/data/control fields affect interrupt routing. Wrong extraction or update logic can cause lost, repeated, or misrouted interrupts.
- AER, DPC, Root Port PIO, and ESM fields are diagnostic and recovery surfaces. Incorrect handling can hide fatal/nonfatal errors, misidentify sources, or disrupt containment/recovery flows.
- ACS, multicast, and VC controls affect routing, peer-to-peer behavior, isolation, and traffic classes. Incorrect masks can violate IOMMU/hypervisor assumptions or break traffic arbitration.
- L1 PM Substate and LTR/OBFF fields affect link power management. Incorrect values can cause resume latency, link instability, or power-state transition races.
- Per-lane equalization definitions are mechanically repeated. A lane-specific generator mismatch can appear only on certain widths or board topologies, while the chunk boundary can falsely look like an incomplete lane set.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing or renamed generated symbols used by consumers.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should fit the register width, masks should not overlap unexpectedly within a register, reserved fields should cover documented gaps, and repeated lane definitions should match except for lane number.
- Cross-check `BIFPLR3_1` and `BIFPLR4_1` register names against sibling default/address headers so every field layout maps to a known register and default value.
- Runtime probe on supported hardware should show stable PCI bridge/root-port enumeration, correct class/capability data, sane bus-number and memory/I/O windows, and expected command-bit transitions.
- Interrupt validation should cover MSI enablement, message address/data programming, masking behavior where supported, and absence of lost or spurious interrupts.
- PCIe link validation should cover negotiated speed/width, link-control-2 target speed handling, link-control-3 equalization triggers, lane error status, and per-lane equalization preset readback across cold boot, warm reset, and resume.
- Error-path validation should use fault injection or observed hardware faults to confirm AER, DPC, Root Port PIO, ESM, header-log, prefix-log, and source-ID fields decode correctly and that diagnostic evidence is not cleared accidentally.
- Power-management tests should verify LTR/OBFF and L1 PM Substate programming across suspend/resume and runtime power transitions, including timeout handling for links that do not converge.
- Virtualization/isolation tests should cover ACS policy, peer-to-peer routing behavior, multicast filters, VC negotiation, and interaction with IOMMU/hypervisor expectations.

### subset-b-003093: lines 61423-63822

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 61423-63822

## Scope

This chunk covers generated AMD NBIO 7.0 PCIe configuration-space shift and mask macros. It starts in the middle of the `BIFPLR4_1_PCIE_LANE_7_EQUALIZATION_CNTL` field set, continues through the tail of the `BIFPLR4_1` PCIe root-port enhanced capabilities, then enters `addressBlock: nbio_pcie0_bifplr5_cfgdecp` and defines most of the `BIFPLR5_1` PCI/PCIe bridge configuration header and capability field masks. The range contains 2,173 `#define` entries across 225 register records.

This file section is data only. It defines preprocessor constants for register bit positions and masks; it has no C functions, structs, variables, runtime storage, or executable control flow.

## Purpose

The chunk supplies the bit-level ABI between AMDGPU NBIO code and NBIO 7.0 PCIe hardware registers. Each field is represented using the standard generated register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the field bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the mask used to isolate, clear, or compose the field.

The matching `nbio_7_0_offset.h` and `nbio_7_0_smn.h` headers provide register addresses and SMN/PCIe access paths; this header provides the bit layout consumed by helper macros such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_FIELD15`, `RREG32_SOC15`, `WREG32_SOC15`, and `RREG32_PCIE`.

## Important Macro Families

### BIFPLR4 PCIe Capability Tail

The first part of the chunk finishes the `BIFPLR4_1` PCIe port capability area:

- Lane equalization control for lanes 7 through 15, with downstream/upstream TX presets and RX preset hints. The adjacent previous chunk contains lanes 0 through part of lane 7.
- ACS enhanced capability fields: capability-list header, supported access-control services, and enable bits for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, and direct translated peer-to-peer.
- Multicast capability fields: maximum group count, ECRC regeneration support, enable/group count, base address, receive vectors, block-all vectors, untranslated-block vectors, and overlay BAR fields.
- L1 PM Substates capability/control fields: PCI-PM and ASPM L1.1/L1.2 support/enables, common-mode restore time, LTR L1.2 threshold value/scale, and T_POWER_ON value/scale.
- Downstream Port Containment fields: DPC capability, trigger/completion control, interrupt enable/status, poisoned TLP egress blocking, software trigger, root-port PIO log size, busy/status, and error source ID.
- Root Port PIO status/mask/severity/system-error/exception fields for config, I/O, and memory unsupported-request completions, completer-abort completions, and completion timeouts.
- Root-port TLP header, implementation-specific, and prefix log registers.
- ESM capability fields: capability-list and vendor header registers, minimum time in electrical idle, ESM enable/control, and supported rate bitmaps from 8.0 GT/s through 28.0 GT/s across `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`.

The `BIFPLR4_1_PCIE_ESM_CTRL` fields are especially relevant to link-speed reporting: `ESM_GEN_3_DATA_RATE`, `ESM_GEN_4_DATA_RATE`, and `ESM_ENABLED` encode alternate PCIe speed values when ESM is active.

### BIFPLR5 PCI/PCIe Bridge Header

At line 62246 the chunk switches to `nbio_pcie0_bifplr5_cfgdecp`. The first `BIFPLR5_1` groups mirror a PCI-to-PCI bridge configuration header:

- Identity/classification: vendor ID, device ID, revision ID, programming interface, subclass, base class, header type/device type, BIST, cache line size, and latency timer.
- Command/status: I/O and memory access enables, bus mastering, special cycles, memory-write-invalidate, parity/SERR controls, fast back-to-back, interrupt disable, interrupt status, capability-list presence, target/master abort, system-error, parity-error, and DEVSEL timing fields.
- Bus/window registers: primary/secondary/subordinate bus numbers, secondary latency timer, I/O base/limit and high halves, memory base/limit, prefetchable memory base/limit and upper halves.
- Interrupt and bridge control: capability pointer, interrupt line/pin, parity/SERR/ISA/VGA/master-abort/secondary-bus-reset/fast-B2B bridge controls, and an extended I/O port 0x80 enable field.

These definitions model what the host PCI core and AMDGPU bridge-management paths see when reading or programming the NBIO root-port bridge function.

### Power Management, MSI, SSID, and Vendor Capabilities

The chunk defines conventional PCI capability records for `BIFPLR5_1`:

- PMI capability and status/control: version, PME clock/support, device-specific init, auxiliary current, D1/D2 support, PME support, power state, no-soft-reset, PME enable/status, data select/scale, B2/B3 support, bus power enable, and PMI data.
- MSI capability: capability header, MSI enable, multiple-message capability/enable, 64-bit support, per-vector masking capability, message address low/high, and message data for 32-bit and 64-bit forms.
- SSID capability: subsystem vendor ID and subsystem ID.
- MSI map capability: enable/fixed/capability type and low/high mapping address fields.
- Vendor-specific enhanced capability: enhanced-capability header plus VSEC ID, revision, length, and two scratch registers.

These masks are consumed indirectly by PCIe/NBIO initialization, diagnostics, and any code that needs to decode or emulate the NBIO bridge capability space.

### PCIe Device, Link, Slot, Root, and Secondary Capability Fields

The `BIFPLR5_1_PCIE_*` definitions cover the core PCI Express capability and several enhanced capabilities:

- PCIe capability header and capability fields: version, device type, slot implemented, and interrupt message number.
- Device capability/control/status: max payload support/size, phantom functions, extended tag, L0s/L1 acceptable latency, role-based error reporting, captured slot power limit/scale, FLR capability, correctable/nonfatal/fatal/unsupported-request reporting enables, relaxed ordering, no-snoop, max read request size, bridge config retry, and pending/error status bits.
- Link capability/control/status: speed, width, PM support, exit latencies, clock power management, surprise-down/DL-active/link bandwidth notification support, ASPM optionality, port number, PM control, retrain/disable/common-clock/extended-sync/autonomous width and bandwidth interrupt controls, current speed/width, training, slot clock config, data-link active, and bandwidth status.
- Slot capability/control/status: attention/power/MRL/presence/hotplug/interlock fields, slot power limit and scale, indicator/power-controller controls, command-completed and DL-state-change interrupts/status.
- Root capability/control/status: SERR enables, PM interrupt enable, CRS software visibility, PME requestor/status/pending.
- PCIe 2.0+ secondary fields: completion-timeout, ARI, atomic operation, IDO, LTR, OBFF, end-to-end TLP prefix, target link speed, compliance and equalization controls/status, supported link speeds, lane error status, and link control 3 equalization request bits.

Lane equalization is fully represented for BIFPLR5 lanes 0 through 15, using the same four fields per lane: downstream TX preset, downstream RX preset hint, upstream TX preset, and upstream RX preset hint.

### Virtual Channel, Serial Number, AER, and Error Reporting

The BIFPLR5 enhanced capability area also includes:

- Virtual Channel capability/control/status for port VC state and VC0/VC1 resource capabilities, controls, traffic-class mapping, arbitration, VC ID, enable, and negotiation-pending status.
- Device serial number low/high dwords.
- Advanced Error Reporting capability header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, header logs, TLP prefix logs, root error command/status, and error source ID.
- DPC and Root Port PIO blocks matching the BIFPLR4 definitions, including trigger controls/status, DPC source ID, PIO masks/severity/system-error/exception bits, and header/prefix logs.

The error-field macros are risk-sensitive because status, mask, severity, and reporting-command registers share similar field names but different semantics. For example, a `_STATUS` bit records an event, a `_MASK` bit suppresses reporting, and a `_SEVERITY` bit changes fatal/nonfatal classification.

### ACS, Multicast, L1 PM Substates, and ESM for BIFPLR5

The BIFPLR5 tail repeats the ACS, multicast, L1 PM substates, DPC/RP-PIO, and ESM capability families:

- ACS capability/control mirrors source validation, translation blocking, peer-to-peer redirect, upstream forwarding, egress control, and direct translated peer-to-peer fields.
- Multicast mirrors group count, enable, address, receive, block, untranslated-block, and overlay BAR fields.
- L1 PM Substates mirror L1.1/L1.2 PCI-PM and ASPM support/enables plus restore time, LTR threshold, and power-on timing fields.
- ESM capability/header/status/control and supported-rate bitmaps are present through `BIFPLR5_1_PCIE_ESM_CAP_3` in this chunk; the range ends before the masks for the later ESM capability registers are complete.

## Control Flow and State Behavior

There is no software control flow in this header. Its effect is compile-time: included C files expand these constants into reads, writes, field extraction, and field composition for 32-bit MMIO/PCIe register values.

The persistent state described by this chunk lives in hardware configuration registers, not in the header. Some fields are durable configuration, such as command register enables, bridge windows, link controls, ACS controls, VC resource controls, multicast tables, L1 PM controls, MSI programming, and ESM enable/rate fields. Others are hardware status or sticky error state, such as PCI status bits, device/link/slot/root status, AER status, DPC status, root-port PIO status, lane error status, and TLP header/prefix logs.

Several fields are action-like controls or event clear/reporting knobs. Examples include link retrain, secondary bus reset, DPC software trigger, DPC interrupt enable/status, AER root error command, slot command completed interrupt enable/status, and L1 PM state enables. Correct sequencing, polling, and clearing rules are enforced by the owning driver paths and PCIe hardware specification; the masks themselves only encode bit placement.

## Dependencies and Integration Points

Direct dependencies are the generated NBIO register header set:

- `nbio_7_0_offset.h` supplies the register identifiers and offsets corresponding to these field names.
- `nbio_7_0_default.h` supplies generated reset/default values where available.
- `nbio_7_0_smn.h` supplies SMN/PCIe address constants used by `RREG32_PCIE`/`WREG32_PCIE` paths.

Observed source-tree integration points include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, which includes this header and uses NBIO field masks with SOC15 register helpers for doorbells, HDP remapping, memory-controller access, interrupt control, clock gating, and PCIe/NBIO management.
- `drivers/gpu/drm/amd/amdgpu/soc15.c`, which includes this header as part of SOC15 ASIC bring-up, reset, PCIe, and interrupt initialization support.
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`, which includes the NBIO 7.0 default/offset/mask headers for SMU10 power-management code.
- SMU PCIe link-speed paths in `arcturus_ppt.c`, `aldebaran_ppt.c`, and `smu_v13_0_6_ppt.c` read `smnPCIE_ESM_CTRL` and manually decode the same bit layout represented here: bit 15 is ESM enabled and bits 8:14 carry the Gen4 ESM data rate offset. Those call sites currently use literal shifts/masks instead of these generated `PCIE_ESM_CTRL` field names.
- Linux PCI/PCIe infrastructure indirectly depends on equivalent semantics when enumerating or configuring the AMD root-port bridge: command/status, bridge windows, MSI, PM, PCIe device/link/slot/root capabilities, AER, ACS, DPC, VC, and L1 PM registers follow standard PCIe capability layouts even though this generated header is AMD-internal.

## Risks

- Bitfield drift can cause severe PCIe failures. A wrong shift or mask can enable the wrong command bit, misprogram bridge address windows, corrupt link training/equalization controls, mask real AER/DPC errors, or misreport link speed/state.
- Repeated capability families are mechanically fragile. BIFPLR4 and BIFPLR5 share many similarly named ACS, MC, L1 PM, DPC, RP-PIO, ESM, and lane-equalization definitions, but they refer to different port instances.
- Status, mask, severity, and control registers are easy to confuse. AER and RP-PIO fields reuse error names across `_STATUS`, `_MASK`, `_SEVERITY`, `_SYSERROR`, and `_EXCEPTION` registers with distinct behavior.
- Power-management and link-management fields interact with firmware and the PCIe link partner. Incorrect L1 substates, target link speed, equalization, retrain, clock power management, or ESM programming can produce performance loss, link instability, or suspend/resume failures.
- ACS and multicast controls affect transaction routing and isolation. Incorrect peer-to-peer redirect, translation blocking, egress control, or multicast block/receive vectors can break DMA routing or isolation assumptions.
- The chunk boundaries split complete definitions: it starts after part of lane 7 equalization has already been defined and ends inside the BIFPLR5 ESM capability bitmap family. The final merged document should connect adjacent chunks for complete lane and ESM coverage.

## Test and Validation Signals

Useful validation signals are build coverage plus hardware/PCIe integration tests:

- Compile AMDGPU and SMU code that includes `nbio_7_0_sh_mask.h`; missing or renamed generated fields should fail at build time in `nbio_v7_0.c`, `soc15.c`, and SMU include users.
- PCI enumeration should show stable bridge vendor/device/class, command/status, bus numbers, bridge windows, MSI, PM, PCIe, AER, ACS, DPC, VC, serial-number, and L1 PM capabilities.
- Link-speed and link-width tests should cover normal PCIe link status plus ESM-enabled reporting paths where `PCIE_ESM_CTRL` overrides conventional speed decoding.
- Suspend/resume and runtime power tests should exercise L1 PM Substates, PME, clock power management, link retrain, and DPC/AER status preservation or clearing.
- Error-injection or platform AER tests should verify uncorrectable/correctable error status, masks, severity, root error command/status, source IDs, header logs, TLP prefix logs, DPC trigger/status, and RP-PIO status/mask/severity behavior.
- SR-IOV or peer-to-peer DMA validation should cover ACS controls, multicast fields, egress/block vectors, and transaction-routing behavior when supported by the platform.
- PCIe compliance or signal-integrity tests should exercise lane equalization presets/hints, lane error status, link control 2/3, and equalization status fields for all BIFPLR5 lanes.

## Unresolved Cross-Chunk References

This chunk begins after the `BIFPLR4_1_PCIE_LANE_7_EQUALIZATION_CNTL` comment and several lane-7 shift definitions, so the adjacent previous chunk owns the beginning of that register group. This chunk ends after the shift definitions and first mask for `BIFPLR5_1_PCIE_ESM_CAP_3`, before the rest of its masks and the following ESM capability registers. The merge/reconciliation lane should stitch those boundaries to produce a complete per-file report.

### subset-b-003094: lines 63823-66205

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 63823-66205

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register shift/mask header. It provides C preprocessor constants for bitfield extraction and update across three adjacent register-map regions:

- the tail of `BIFPLR5_1_PCIE_ESM_CAP_3` plus `BIFPLR5_1_PCIE_ESM_CAP_4` through `BIFPLR5_1_PCIE_ESM_CAP_7`;
- the full `nbio_pcie0_bifplr6_cfgdecp` address block, exposed as `BIFPLR6_1_*` PCIe bridge/root-port configuration-space fields;
- the beginning of `nbio_pcie0_bifp0_pciedir_p`, exposed as `BIFP0_*` direct PCIe port control, transmit, receive, flow-control, and error-control fields through the start of receive-credit allocation.

The file is hardware-description data, not executable driver logic. Its purpose is to give AMDGPU NBIO code stable symbolic names for hardware bit positions and masks instead of hard-coded numeric constants. Address headers provide the register offsets; this `*_sh_mask.h` header provides the register field layout.

## Register Families Covered

The opening lines finish the `BIFPLR5_1` Equalization Service/Extended Speed Mode capability bitmap. `BIFPLR5_1_PCIE_ESM_CAP_3` covers the remaining `ESM_14P1G` through `ESM_15P9G` masks after the chunk starts mid-register. `BIFPLR5_1_PCIE_ESM_CAP_4` maps `ESM_16P0G` through `ESM_18P9G`, `CAP_5` maps `ESM_19P0G` through `ESM_21P9G`, `CAP_6` maps `ESM_22P0G` through `ESM_24P9G`, and `CAP_7` maps `ESM_25P0G` through `ESM_26P3G`. These are one-bit advertised capability entries, with matching `__SHIFT` and `_MASK` constants for each speed point.

The `BIFPLR6_1_*` section is a complete PCIe root-port/bridge configuration decode block. It starts with conventional PCI identity and bridge header fields: vendor and device ID, command and status, revision/class code fields, cache line, latency, header, BIST, primary/secondary/subordinate bus numbering, I/O and memory base/limit windows, prefetchable windows, upper base/limit halves, capability pointer, interrupt line/pin, bridge control, and extended bridge control. It then describes the capability chain for power management, PCI Express device/link/slot/root capabilities and controls, MSI, SSID, MSI mapping, vendor-specific enhanced capability, virtual channel resources, device serial number, Advanced Error Reporting, secondary PCIe extended capability, lane equalization controls for lanes 0 through 15, ACS, multicast, L1 PM substates, Downstream Port Containment, RP PIO status/mask/severity/logging, and the `BIFPLR6_1_PCIE_ESM_*` capability group.

The `BIFP0_*` section switches from PCIe config-space description to the direct PCIe port register view. This chunk includes `BIFP0_PCIEP_RESERVED`, `BIFP0_PCIEP_SCRATCH`, `BIFP0_PCIEP_PORT_CNTL`, transmit control and request accounting (`BIFP0_PCIE_TX_CNTL`, requester ID, vendor-specific fields, request number control, sequence and replay state, ACK latency limit), transmit credit advertise/init/status registers, flow-control update thresholds, physical lane status, received flow-control credit snapshots, PCIe error-control knobs, receive filtering/control (`BIFP0_PCIE_RX_CNTL` and `RX_CNTL3`), receive expected sequence number, vendor-specific receive status, and the first lines of `BIFP0_PCIE_RX_CREDITS_ALLOCATED_P`.

## Important APIs, Types, And Constants

There are no functions, structs, enums, or runtime APIs in this slice. The consumed interface is the macro naming convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit index for a register field.
- `<REGISTER>__<FIELD>_MASK` gives the unshifted mask for that field.
- `BIFPLR5_1`, `BIFPLR6_1`, and `BIFP0` identify distinct NBIO/PCIe register namespaces and must not be treated as interchangeable even when field names resemble standard PCIe fields.

Important `BIFPLR6_1` groups include PCI command bits (`IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`, `SERR_EN`, `INT_DIS`), bridge bus/window registers (`PRIMARY_BUS`, `SECONDARY_BUS`, `SUB_BUS`, I/O and memory base/limit fields), power-management controls (`POWER_STATE`, `PME_EN`, `PME_STATUS`, data select/scale), PCIe device control (`CORR_ERR_EN`, `NON_FATAL_ERR_EN`, `FATAL_ERR_EN`, `USR_REPORT_EN`, `MAX_PAYLOAD_SIZE`, `MAX_READ_REQUEST_SIZE`), link controls/status (`PM_CONTROL`, `LINK_DIS`, `RETRAIN_LINK`, negotiated speed/width, bandwidth status), slot and root controls, MSI message address/data fields, virtual-channel arbitration and resource fields, lane equalization presets/cursors for lanes 0-15, ACS source validation/translation/blocking bits, multicast address/block/overlay BAR fields, L1 PM substate timing and enable fields, DPC control/status, RP PIO status/masks/severity/sys-error/exception fields, and ESM status/control/capability bits.

The AER block is particularly important for error handling. `BIFPLR6_1_PCIE_UNCORR_ERR_STATUS`, `_MASK`, and `_SEVERITY` use related field names for DLP, surprise down, poisoned TLP, flow-control protocol, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal uncorrectable error, MC blocked TLP, AtomicOp egress blocked, and TLP prefix blocked events. Correctable error status/mask fields include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory nonfatal, corrected internal error, and header-log overflow. Header and TLP-prefix log registers are full-width fields.

Important `BIFP0` fields cover direct port behavior rather than standard config-space presentation. `BIFP0_PCIEP_PORT_CNTL` gates slave-port requests, hotplug/PME behavior, completion allocation, completion payload sizing, and poisoned unsupported-request response mode. `BIFP0_PCIE_TX_CNTL` controls transmit ordering/no-snoop overrides, packet packing, TLP flushing, completion/non-posted pass behavior, power-management request clearing, and flow-control update timeout handling. The transmit credit registers expose advertised and initialized posted, non-posted, and completion data/header credits, and `BIFP0_PCIE_TX_CREDITS_STATUS` reports per-class credit errors and current status. `BIFP0_PCIE_ERR_CNTL` can disable error reporting, select first-received error logging behavior, drop ECRC failures, deliberately generate LCRC/ECRC errors, tune AER header-log timeout behavior, inspect/halt slave buffers, and force immediate error messaging. `BIFP0_PCIE_RX_CNTL` contains many receive-side ignore toggles for malformed or unsupported TLP classes, completion timeout controls, PASID/prefix error handling, TPH disable, and FLR timeout behavior; `BIFP0_PCIE_RX_CNTL3` extends this to root-complex PASID and invalidation request unsupported-request cases.

## Control Flow

This chunk has no direct control flow. It influences driver control flow when AMDGPU code performs register reads, masks fields, builds read/modify/write values, or decodes hardware state for logging and diagnostics. The common pattern is: read a register using the address macro from the corresponding NBIO register header, clear or test the relevant `_MASK`, shift values by the matching `__SHIFT`, then write or interpret the result.

Ordering in this file follows the hardware register map. The transition at `nbio_pcie0_bifplr6_cfgdecp` begins a complete configuration-space layout for `BIFPLR6_1`; the transition at `nbio_pcie0_bifp0_pciedir_p` begins direct PCIe port registers. Adjacent chunks are needed for full file-level control reasoning because this slice starts mid-`BIFPLR5_1_PCIE_ESM_CAP_3` and ends mid-`BIFP0_PCIE_RX_CREDITS_ALLOCATED_P`.

## State And Persistence Behavior

The header itself has no mutable software state and persists nothing. The described state is in GPU NBIO/PCIe hardware registers. Some fields are configuration state programmed by firmware, the kernel PCI core, or AMDGPU, such as command enables, bus/window ranges, bridge controls, MSI fields, PCIe device/link controls, VC resource controls, ACS controls, L1 PM substate controls, DPC control, ESM control, direct port control, TX/RX policy bits, and error-control knobs. Other fields are hardware capability, status, counter, or log state, such as vendor/device IDs, capability IDs and next pointers, link status, lane equalization status, AER status and header logs, DPC trigger/status/source IDs, RP PIO logs, sequence/replay state, credit status, lane reversal/width status, and receive expected sequence number.

Persistence and side effects are defined by the ASIC register specification and PCIe rules, not by these macros. Many PCIe status and AER fields are latched or write-one-to-clear in hardware, while control fields may reset on function, link, bus, or GPU reset boundaries. Full-width log and address fields can be read-only, writeable, or side-effectful depending on the underlying register; this header only gives bit positions and masks and does not encode access type, reset values, write constraints, or sequencing requirements.

## Dependencies And Integration Points

This file is included by AMDGPU NBIO register-access code in the Ceph-client Linux kernel source mirror. It integrates with adjacent generated headers for NBIO 7.0 register offsets, with AMDGPU MMIO or indirect-register helpers, and with Linux PCI/PCIe subsystem concepts. The `BIFPLR6_1` config-decode definitions mirror architectural PCIe capability structures that must stay coherent with PCI core expectations for bridge configuration, MSI, power management, AER, ACS, DPC, L1 PM substates, and link training. The `BIFP0` direct-register definitions are more ASIC-specific and integrate with GPU reset, link bring-up, error injection/diagnostics, flow-control tuning, and low-level PCIe transport handling.

The ESM capability bitmaps are integration points for any code or firmware that advertises, validates, or programs supported PCIe link speed/equalization modes. The repeated capability-list and enhanced-capability fields are also integration points for debug tooling and register dumps because they allow raw NBIO values to be decoded into PCIe-visible state.

## Risks And Edge Cases

Generated-register drift is the main risk. A wrong shift or mask can make driver code silently set the wrong bit, clear reserved bits, mis-size a bridge window, enable/disable the wrong PCIe behavior, misreport link capabilities, or decode error status incorrectly. The risk is higher in this chunk because many fields are repeated across status, mask, severity, and log registers with very similar names.

Write paths must preserve reserved and unrelated bits unless the ASIC documentation explicitly permits whole-register writes. Several registers pack many single-bit controls into one word, while log/address/data registers use full-width `0xFFFFFFFFL` masks. Treating all macros as equally writeable is unsafe: capability IDs, next pointers, status, logs, lane status, credit status, and sequence state may be read-only or have write-clear semantics.

The `BIFPLR6_1_PCIE_UNCORR_ERR_*`, `PCIE_CORR_ERR_*`, `PCIE_DPC_*`, and `PCIE_RP_PIO_*` groups are semantically close but target different error-handling layers. Using a status mask against a severity or mask register may compile because the bit positions align, but it changes behavior. Direct error-injection or error-generation fields in `BIFP0_PCIE_ERR_CNTL` are also hazardous outside validation contexts because they can deliberately create link-layer or end-to-end CRC failures.

Chunk boundaries matter for reconciliation. The first visible register in this slice is incomplete because the matching `BIFPLR5_1_PCIE_ESM_CAP_3` shifts and the `ESM_14P0G` mask are just before line 63823. The final visible register is also incomplete because only the first `BIFP0_PCIE_RX_CREDITS_ALLOCATED_P` definitions appear before line 66205; the NP/CPL receive-credit allocation registers and later direct-port registers are in the following chunk.

## Test Signals

There are no unit tests local to this generated header. Useful validation signals are build, static comparison, and hardware behavior:

- Full kernel or AMDGPU builds catch malformed macro names, missing includes, and syntax errors after generated-header changes.
- Generator-output review should compare this chunk against the authoritative NBIO 7.0 register database, especially repeated AER/DPC/RP-PIO fields, ESM capability ranges, lane equalization fields, and `BIFP0` direct-port controls.
- PCI config-space dumps and register dumps can validate that decoded `BIFPLR6_1` bridge, capability, MSI, AER, ACS, DPC, L1 PM, and ESM fields match expected hardware values.
- Link bring-up, retraining, hotplug/PME, ASPM/L1 substate, and bandwidth-change logs are practical signals for the device/link/slot/root control fields.
- AER or PCIe error-injection validation can confirm uncorrectable/correctable status, mask, severity, header-log, DPC, RP-PIO, and `BIFP0_PCIE_ERR_CNTL` behavior.
- Flow-control and stability tests under posted, non-posted, and completion traffic pressure can exercise TX credit advertise/init/status fields, FCU thresholds, RX timeout/ignore controls, and credit allocation decoding.

### subset-b-003095: lines 66206-68539

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 66206-68539

## Scope

This chunk covers generated NBIO 7.0 PCIe register shift/mask definitions for AMDGPU. The range starts inside the `BIFP0_PCIE_RX_CREDITS_ALLOCATED_P` family, continues through the rest of the BIFP0 PCIe-port field map, covers the complete BIFP1 PCIe-port field map, and then covers the start of BIFP2 through the first four shift definitions of `BIFP2_PCIEP_ERROR_INJECT_PHYSICAL`.

The requested range contains 2,181 `#define` lines: 1,092 `__SHIFT` macros and 1,089 `_MASK` macros across 148 register groups. It is purely a generated hardware bitfield header. There are no C functions, structs, enums, variables, includes, allocation paths, locks, or executable control flow in this slice.

## Purpose

The header provides the bit-level ABI between AMDGPU NBIO/PCIe code and NBIO 7.0 hardware registers. Each field is represented with the generated convention:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset for composing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the field mask used with the shift value.

The matching address side is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`; reset/default values are in `nbio_7_0_default.h`. Runtime code combines those register offsets and these field constants through AMDGPU helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, and `SOC15_REG_OFFSET`.

Although this source path is under a local `ceph-client` mirror, this chunk is AMD GPU PCIe/NBIO register metadata and does not implement Ceph or distributed filesystem behavior.

## Important Macro Families

### BIFP0 Tail

The BIFP0 portion begins with the end of receive credit allocation:

- `BIFP0_PCIE_RX_CREDITS_ALLOCATED_NP` and `_CPL` expose allocated non-posted and completion data/header credits.
- `BIFP0_PCIEP_ERROR_INJECT_PHYSICAL` exposes physical-layer fault injection fields for lane errors, framing errors, bad SKP parity/LFSR, loopback underflow/overflow, deskew errors, 8b/10b errors, SKP ordered-set errors, invalid ordered-set identifiers, and bad sync headers.
- `BIFP0_PCIEP_ERROR_INJECT_TRANSACTION` exposes transaction/link-layer fault injection for flow-control errors, replay-number rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion timeout.
- `BIFP0_PCIEP_NAK_COUNTER` tracks received and generated NAK counts.
- `BIFP0_PCIEP_RX_CAPTURED_LTR_CTRL_STATUS` and `_THRESHOLD_VALUES` expose captured LTR interrupt/status masks and snoop/non-snoop threshold value, scale, and requirement bits.

Most of the BIFP0 coverage is link-controller state:

- `BIFP0_PCIE_LC_CNTL`, `_TRAINING_CNTL`, `_LINK_WIDTH_CNTL`, `_N_FTS_CNTL`, and `_SPEED_CNTL` define controls for link reset, L0s/L1/L23 behavior, receiver idle handling, link training, power state, renegotiation, upconfiguration, dynamic lane power, target/current data rate, software/hardware speed changes, and failed speed-change status.
- `BIFP0_PCIE_LC_STATE0` through `_STATE5` provide packed link-training state fields such as current/previous/next states, timeout state, receiver-detect state, exit-to-PU state, and substate indicators.
- `BIFP0_PCIE_LINK_MANAGEMENT_CNTL2`, `_STATUS`, `_MASK`, and `_CNTL` describe link-management events and interrupts for data-rate, link-width, autonomous bandwidth, bandwidth-management, and target-speed-change conditions.
- `BIFP0_PCIE_LC_CNTL2` through `_CNTL7`, `_BW_CHANGE_CNTL`, `_CDR_CNTL`, `_LANE_CNTL`, `_FORCE_COEFF`, `_BEST_EQ_SETTINGS`, and `_FORCE_EQ_REQ_COEFF` cover equalization, coefficient forcing, directed speed changes, receiver-detect timing, lane reversal, lane disable/turnoff behavior, CDR controls, FOM/phase observation, Gen3 equalization knobs, and test/debug behavior.
- `BIFP0_PCIE_LC_L1_PM_SUBSTATE` and `_SUBSTATE2` expose L1.1/L1.2, T-power-on, common-mode restore, PHY powerup, and related PCIe L1 PM substate controls.

The BIFP0 tail also includes strap and miscellaneous port-side fields:

- `BIFP0_PCIEP_STRAP_LC` and `_STRAP_MISC` describe hardware strap-derived defaults for FTS/TSx counts, SKP interval, receiver-detect bypass, compliance, lane reversal, lane negotiation, E2E prefix, OBFF, and LTR support.
- `BIFP0_PCIE_LC_PORT_ORDER` records port ordering.
- `BIFP0_PCIEP_BCH_ECC_CNTL`, `_HPGI_PRIVATE`, `_HPGI`, `_HCNT_DESCRIPTOR`, and `_PERF_CNTL_COUNT_TXCLK` define BCH/ECC selection, high-priority/general interrupt-style fields, descriptor fields, and a TXCLK performance-count control.

### BIFP1 Complete Port Map

The BIFP1 block starts at `addressBlock: nbio_pcie0_bifp1_pciedir_p` and is complete inside this range. Its early groups define port-local scratch and transmit/receive datapath fields:

- `BIFP1_PCIEP_RESERVED`, `_SCRATCH`, and `_PORT_CNTL` provide reserved/scratch storage and port controls such as client-independent reset, HOLD training flags, link reset, hot-reset generation, bridge enable, end-of-chain, ECRC enable, and transition-to-recovery behavior.
- `BIFP1_PCIE_TX_CNTL`, `_REQUESTER_ID`, `_VENDOR_SPECIFIC`, `_REQUEST_NUM_CNTL`, `_SEQ`, `_REPLAY`, and `_ACK_LATENCY_LIMIT` define TX error handling, packet generation options, replay/sequence state, requester ID, vendor-specific TX data, and ACK latency limits.
- `BIFP1_PCIE_TX_CREDITS_ADVT_*`, `_INIT_*`, `_STATUS`, and `_FCU_THRESHOLD` describe advertised/initial posted, non-posted, and completion credits plus credit error/current-status flags and FCU thresholds for VC0/VC1.
- `BIFP1_PCIE_P_PORT_LANE_STATUS` exposes lane reversal and PHY link width.
- `BIFP1_PCIE_FC_P`, `_FC_NP`, and `_FC_CPL` expose posted, non-posted, and completion flow-control credits.
- `BIFP1_PCIE_ERR_CNTL` defines error reporting disable, first-error logging strap, ECRC drop/generation controls, LCRC generation controls, AER header log timeout, slave-buffer halt status/reset, immediate error-message sending, and poisoned advisory-nonfatal behavior.
- `BIFP1_PCIE_RX_CNTL`, `_EXPECTED_SEQNUM`, `_VENDOR_SPECIFIC`, `_CNTL3`, and `RX_CREDITS_ALLOCATED_*` define RX ignore/NAK/timeout/TPH/PASID behavior, expected sequence number, vendor-specific RX data/status, root-complex PASID unsupported-request handling, and allocated RX credits.

BIFP1 then repeats the same physical error injection, transaction error injection, NAK counter, LTR capture, LC control, LC state, link-management, strap, L1 PM substate, ECC/HPGI/descriptor, and TXCLK performance-count families described above for BIFP0, but with `BIFP1_` register names. Because the BIFP1 address block is complete in this chunk, it is the most self-contained part of the slice.

### BIFP2 Start

The BIFP2 portion starts at `addressBlock: nbio_pcie0_bifp2_pciedir_p` and covers the same early port, TX, credit, FC, error, and RX families as BIFP1:

- `BIFP2_PCIEP_RESERVED`, `_SCRATCH`, `_PORT_CNTL`.
- `BIFP2_PCIE_TX_*` requester, vendor-specific, request-number, sequence, replay, ACK latency, advertised/init credit, credit status, and FCU threshold groups.
- `BIFP2_PCIE_P_PORT_LANE_STATUS`, `PCIE_FC_P`, `PCIE_FC_NP`, and `PCIE_FC_CPL`.
- `BIFP2_PCIE_ERR_CNTL`, `PCIE_RX_CNTL`, `PCIE_RX_EXPECTED_SEQNUM`, `PCIE_RX_VENDOR_SPECIFIC`, `PCIE_RX_CNTL3`, and `PCIE_RX_CREDITS_ALLOCATED_*`.

The chunk ends at lines 68535-68539 after only the first four `BIFP2_PCIEP_ERROR_INJECT_PHYSICAL` shift definitions. The remaining BIFP2 physical error injection masks and later BIFP2 LC/link-management families belong to the next chunk.

## Control Flow

There is no runtime control flow in this header. It influences control flow indirectly because compiled AMDGPU code uses these constants to compose and decode 32-bit MMIO values. The driver supplies all sequencing: PCIe/NBIO initialization, link training, speed and width changes, reset handling, error injection, interrupt mask/status processing, power-state transitions, and diagnostic polling.

Important command-like fields represented here include `LC_RESET_LINK`, `LC_RECONFIG_NOW`, `LC_RENEGOTIATE_EN`, `LC_INITIATE_LINK_SPEED_CHANGE`, `LC_CLR_FAILED_SPD_CHANGE_CNT`, hot-reset generation, error-injection fields, HPGI status/enable/clear-style fields, and link-management interrupt masks. The macros do not say whether a bit is read-only, sticky, write-one-to-clear, self-clearing, strap-derived, or strobe-like; that behavior is defined by hardware and consuming AMDGPU code.

## State And Persistence Behavior

This chunk stores no software state. It describes hardware-backed PCIe/NBIO state for three port instances:

- Link controller configuration and status: reset state, training state, L0s/L1/L23 behavior, link width, negotiated/current speed, renegotiation/upconfiguration support, lane power state, receiver-detect behavior, CDR, equalization, and coefficient forcing.
- Transaction and data-path state: TX/RX credits, flow-control credits, sequence/replay counters, ACK latency limit, requester ID, vendor-specific data/status, expected sequence number, NAK counters, and RX ignore/timeout policies.
- Error and diagnostic state: AER/ECRC/LCRC controls, error reporting disable, error injection controls, link-management status/mask bits, FOM/equalization observation, and BCH/ECC selection.
- Power-management capability/state: LTR capture and thresholds, L1 PM substate controls, strap-derived LTR/OBFF/prefix support, PHY powerup/common-mode restore timing, and transition-to-L0s/L1 controls.
- Port identity and wiring state: lane reversal, lane negotiation, PHY link width, port ordering, bridge/end-of-chain controls, and strap-derived defaults.

Persistence is hardware-defined. Configuration fields generally persist until reset, power gating, reinitialization, or a later driver write. Status counters, link-state fields, captured LTR status, error status, and training/equalization observations can change asynchronously as the PCIe link trains, retrains, enters low-power states, encounters errors, or is reset.

## Dependencies And Integration Points

The direct dependencies are the generated NBIO 7.0 register headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h` supplies matching register offsets for these field names.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h` supplies reset/default values for many of the same register families.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h` supplies SMN-side addresses used by NBIO code outside the normal per-register offset tables.

Primary integration is through AMDGPU NBIO and PCIe helpers. `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c` includes the NBIO 7.0 generated headers and is the ASIC-specific integration point for doorbells, interrupt handling, memory-controller access, SR-IOV-related NBIO state, and PCIe/NBIO register programming. Broader AMDGPU PCIe and power-management paths may use the `PCIE_LC_*`, `PCIE_LINK_MANAGEMENT_*`, `PCIE_RX/TX_*`, and `PCIEP_STRAP_*` fields to validate link capabilities, force or observe speed/width changes, handle error status, and coordinate low-power states.

The BIFP0/BIFP1/BIFP2 duplication is intentional: each port instance has a separate register namespace with similar field layouts. Consumers must pair the right `BIFP<n>` mask constants with the matching `BIFP<n>` offsets; cross-instance mixups can compile cleanly while touching the wrong port.

## Risks And Edge Cases

- Bitfield drift is high impact. A wrong shift or mask can write unrelated PCIe/NBIO fields and cause link-training failures, surprise retrains, incorrect speed/width negotiation, broken low-power entry/exit, lost interrupts, or GPU hangs.
- Repeated port blocks are mechanically fragile. BIFP0, BIFP1, and BIFP2 share many names and layouts, but chunk boundaries are not aligned with complete port families; BIFP0 starts mid-credit group and BIFP2 ends mid-error-injection group.
- Error-injection fields should not be treated as normal error handling. Accidentally enabling physical or transaction error injection can create artificial PCIe faults.
- Link speed/width and equalization controls are sequencing-sensitive. `LC_INITIATE_LINK_SPEED_CHANGE`, target speed overrides, coefficient forcing, CDR settings, receiver-detect controls, and upconfiguration fields must be used only with the correct training and polling sequence.
- RX error-ignore fields can mask real PCIe problems. Overbroad use of `RX_IGNORE_*`, completion timeout disables, PASID unsupported-request ignore bits, or TPH disable can hide protocol errors or change observable fault handling.
- Strap fields describe hardware-derived policy and capability defaults. Treating strap-derived support bits as freely writable runtime policy can desynchronize software assumptions from fused or board-level configuration.
- LTR and L1 PM substate fields affect platform power behavior. Wrong threshold, scale, common-mode restore, PHY powerup, or L1.1/L1.2 settings can produce latency, wake, suspend/resume, or interoperability failures.
- Counters and status fields may be live, sticky, or clear-on-read/write depending on hardware. The generated macro names do not encode those side effects.

## Test And Validation Signals

Useful validation is mostly generated-header consistency plus hardware behavior:

- Build AMDGPU with NBIO 7.0 support enabled; missing or renamed macros should fail in NBIO/PCIe code that includes `nbio_7_0_sh_mask.h`.
- Mechanically compare this shift/mask chunk against AMD's authoritative NBIO 7.0 register database and ensure the same register names exist in `nbio_7_0_offset.h`.
- Verify BIFP instance pairing by checking that BIFP0, BIFP1, and BIFP2 uses reference matching address blocks and do not mix masks from another port instance.
- Exercise PCIe link bring-up, hot reset, GPU reset, suspend/resume, ASPM/L1 PM substates, link retraining, speed changes, and lane-width negotiation on NBIO 7.0 hardware.
- Monitor negotiated link width/speed, link-management status, NAK counters, RX/TX credit status, AER/ECRC/LCRC behavior, and kernel logs for PCIe errors or retraining loops.
- For diagnostics-only paths, validate physical and transaction error-injection programming under controlled tests and confirm that injected errors are reported, masked, or cleared as expected.
- Test LTR/OBFF/prefix/PASID-related behavior where platform support exists, especially around low-power entry/exit and completion timeout handling.

## Cross-Chunk Notes

Adjacent chunks are required for a complete per-file account. The previous chunk owns the beginning of BIFP0 receive-control and posted-credit allocation definitions. The next chunk owns the rest of `BIFP2_PCIEP_ERROR_INJECT_PHYSICAL` plus later BIFP2 LC/link-management/strap/L1 PM fields. The merge lane should avoid treating this document as a complete summary of all BIFP0 or BIFP2 register groups.

### subset-b-003096: lines 68540-70871

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 68540-70871

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register shift/mask header. It defines C preprocessor constants for bit positions and masks used to access PCIe BIF port register fields in the `nbio_pcie0` register space. The content is data-like hardware description, not executable code: every declaration is a `#define` for a `__SHIFT` or `_MASK` constant.

The line range starts inside the `BIFP2_PCIEP_ERROR_INJECT_PHYSICAL` register, continues through the rest of the BIFP2 PCIe link-controller and port-management registers, covers the complete `addressBlock: nbio_pcie0_bifp3_pciedir_p`, and begins `addressBlock: nbio_pcie0_bifp4_pciedir_p` through the physical error-injection masks. These macros are consumed by driver code that pairs shift/mask constants from this header with register-offset constants from companion generated headers and AMDGPU register access helpers.

## Register Areas Covered

The BIFP2 section begins with physical-layer error injection fields for lane, framing, SKP parity/LFSR, loopback underflow/overflow, deskew, 8b/10b disparity/decode, SKP ordered-set, invalid OS identifier, and bad sync header faults. It then defines transaction-layer error injection fields for flow-control errors, replay-number rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion timeout. This is followed by NAK counters and captured LTR threshold/status fields.

Most of the BIFP2 body describes link-controller controls and status: `PCIE_LC_CNTL`, training control, link width control, FTS count, speed control, LC state registers 0 through 5, link-management status/mask/control, bandwidth-change controls, CDR and lane controls, LC control extensions 2 through 7, equalization coefficient forcing/best-settings registers, strap fields, L1 PM substates, port order, BCH ECC, HPGI/private HPGI state, descriptor count, and TX clock performance counting.

The BIFP3 address block is a full repeated port block. It starts at `nbio_pcie0_bifp3_pciedir_p` and covers reserved/scratch/port control, TX controls and requester/vendor-specific fields, request numbering, sequence/replay/ack-latency registers, advertised/initial/current TX credit registers, lane status, flow-control credit visibility, PCIe error control, RX controls, expected sequence number, vendor-specific RX fields, RX control 3, allocated RX credits, physical and transaction error injection, NAK counters, captured LTR, link-controller controls/status, strap fields, L1 substates, HPGI, descriptors, and TX clock performance counting.

The BIFP4 section starts another repeated port block. In this chunk it includes reserved/scratch/port control, TX control/requester/vendor/request-number/sequence/replay/ack-latency fields, TX credit advertise/init/status/FCU thresholds, port lane status, FC P/NP/CPL fields, PCIe error control, RX controls, expected sequence number, vendor-specific RX fields, RX control 3, allocated RX credits, and the beginning of physical error injection. Later BIFP4 link-controller and management registers are outside this chunk.

## Important APIs, Types, And Constants

There are no functions, structs, enums, callbacks, or runtime APIs in this range. The exported interface is the macro naming convention:

- `BIFP{N}_<REGISTER>__<FIELD>__SHIFT` gives the field's least-significant bit position.
- `BIFP{N}_<REGISTER>__<FIELD>_MASK` gives the unshifted 32-bit register mask for that field.
- `BIFP2`, `BIFP3`, and `BIFP4` identify repeated PCIe BIF port instances. The field layouts are intentionally very similar across ports, but the macro prefixes bind each definition to a distinct hardware register instance.

Important field families in this chunk include link training and power-management controls (`LC_TRAINING_CNTL`, `LC_POWER_STATE`, L0s/L1/L23 entry and wake controls), link width and reconfiguration controls (`LC_LINK_WIDTH`, `LC_RECONFIG_NOW`, upconfigure/renegotiate controls, lane power state), link speed controls (`LC_GEN2_EN_STRAP`, `LC_GEN3_EN_STRAP`, target speed override, software/hardware speed-change forcing, current data rate, advertised data rate), interrupt-style link-management status/mask bits, and bandwidth hint/control fields.

The TX/RX credit and flow-control fields expose advertised, initialized, allocated, and current/error credit state for posted, non-posted, and completion classes. The error-control fields include reporting disable, ECRC/LCRC generation or drop behavior, AER header-log timeout, slave-buffer halt status/reset, and immediate error-message sending. The RX controls include ignore bits for multiple TLP/config/completion/error classes, NAK-on-FIFO-full, one-shot NAK generation, flow-control initialization from registers, completion timeout controls, PASID/prefix error ignore controls, TPH disable, and FLR timeout disable.

## Control Flow

This chunk has no direct control flow. It participates in control flow only through code that performs register read/modify/write operations. A typical consumer reads a 32-bit NBIO register, clears a field with `~*_MASK`, inserts the shifted field value with `(value << *_SHIFT) & *_MASK`, and writes the result back through AMDGPU's MMIO or indexed-register access path.

The file ordering follows the generated hardware register map, not program execution order. Within each register group, `__SHIFT` constants appear before corresponding `_MASK` constants. BIFP3 repeats the same conceptual sequence as surrounding BIF port blocks, while BIFP2 and BIFP4 are partial in this chunk because the chunk boundaries fall inside their generated address-block coverage.

## State And Persistence Behavior

The header itself contains no mutable software state and persists nothing. The described state lives in NBIO PCIe hardware registers. Some fields are software-programmed controls, including reset/link-training controls, speed/width renegotiation controls, ASPM and L1 substate controls, error reporting masks, RX ignore behavior, MSI-like interrupt/status masking for link-management events, and error injection controls. Other fields are hardware-owned status or counters, including LC state fields, NAK counters, link-management status, current data rate, lane status, credit status, expected sequence number, and captured LTR thresholds.

Persistence and side effects are hardware-defined. Many status bits may be latched, write-one-to-clear, self-clearing, strap-derived, or reset by link state transitions. The shift/mask macros do not encode access type, reset value, volatility, self-clear behavior, or sequencing requirements. Any driver write path using these constants must preserve unrelated/reserved bits unless companion register documentation explicitly permits a full-register write.

## Dependencies And Integration Points

This header is one generated member of the AMDGPU ASIC register interface. Register address headers provide offsets, this `*_sh_mask.h` header provides bit layouts, and driver C code supplies access primitives, synchronization, and hardware sequencing. The chunk integrates with AMDGPU NBIO, PCIe link management, GPU reset and recovery, runtime power management, error handling, and ASIC bring-up or diagnostics code.

The field names map closely to PCIe concepts: link training state machine, ASPM/L1 substates, lane width negotiation, Gen2/Gen3 speed negotiation, flow-control credits, DLLP/TLP replay/NAK behavior, completion timeouts, ECRC/LCRC handling, latency tolerance reporting, and physical/transaction-layer error injection. Because the macros are port-specific, consumers must select the correct BIFP instance for the physical port or virtualized topology being inspected or programmed.

## Risks And Edge Cases

The main risk is register-map drift. A wrong shift or mask in this generated header can silently program the wrong hardware bit, clear adjacent status, disable error reporting, force unsafe link retraining, or misdecode link/credit/error telemetry. Repeated BIFP blocks increase review difficulty because near-identical definitions are expected, but an incorrect prefix or copied field can still target the wrong port.

Chunk boundaries are material for later merge work. This range starts after the `BIFP2_PCIEP_ERROR_INJECT_PHYSICAL` comment and begins with its remaining field definitions; the earlier BIFP2 registers are in previous chunks. Conversely, this range ends before completing BIFP4 physical error injection and before BIFP4 transaction error injection, link-controller, strap, L1 substate, and HPGI definitions. File-level conclusions about all BIF ports must reconcile adjacent chunk reports.

Error-injection and error-control fields are especially sensitive. Test or diagnostic code that writes the `ERROR_INJECT_*`, LCRC/ECRC generation, RX ignore, or reporting-disable bits can mask real PCIe problems or intentionally create link faults. These paths should be guarded by debug/validation-only policy and sequenced with recovery handling. Credit, sequence, NAK, and link-management status fields should also be treated as volatile hardware state, so stale snapshots can mislead diagnostics.

## Test Signals

There are no unit tests in this header. Useful validation signals are build, static, and hardware-facing:

- Full kernel or AMDGPU builds catch malformed macro names, missing companion definitions, or syntax regressions.
- Generated-header diffs should be compared against the authoritative NBIO 7.0 register database, especially across BIFP2/BIFP3/BIFP4 repetition and this chunk's partial boundaries.
- Register dumps decoded with these masks should match expected link width, speed, LC state, LTR, credit, NAK, and error-control state on known boards.
- Link retraining, ASPM/L1 substate, reset/recovery, and runtime-power tests can reveal incorrect control masks through failed transitions or unexpected link-down behavior.
- PCIe AER/error-injection validation can exercise transaction/physical error-injection, RX ignore, ECRC/LCRC, completion-timeout, and reporting-disable fields, while checking that recovery and telemetry decode the intended bits.

### subset-b-003097: lines 70872-73204

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 70872-73204

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 register shift/mask header. It contains C preprocessor constants only: `#define` names ending in `__SHIFT` or `_MASK` that describe bit positions and bit masks for NBIO PCIe/BIF port registers. There are no functions, structs, enums, branches, allocation sites, or runtime side effects in this range.

The requested range starts inside the tail of `BIFP4_PCIEP_ERROR_INJECT_PHYSICAL`, then covers the rest of the BIFP4 PCIe port register field map. It fully covers the `nbio_pcie0_bifp5_pciedir_p` address block and begins the `nbio_pcie0_bifp6_pciedir_p` address block, ending partway through `BIFP6_PCIEP_ERROR_INJECT_TRANSACTION`. In total, the range contains 2,182 `#define` entries grouped by 147 comment markers.

The purpose of these definitions is to let NBIO, PCIe, and diagnostics code manipulate hardware registers by symbolic field names instead of hard-coded bit arithmetic. The companion NBIO offset/SMN headers provide register addresses; this `*_sh_mask.h` file provides the field layout needed by helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD`.

## Register Areas Covered

The BIFP4 portion continues the physical-layer error injection register and then covers transaction-layer error injection, NAK counters, captured LTR control/status and threshold values, link-control registers, link-training controls, lane-width controls, speed controls, link-state status registers, link-management status/mask/control registers, strap registers, L1 power-management substate controls, BCH ECC controls, HPGI controls, descriptor fields, and a TXCLK performance counter control.

The BIFP5 block is complete for this slice. It starts with reserved/scratch and port-control registers, then covers TX request control, requester ID, vendor-specific fields, request-number and replay/sequence tracking, advertised and initial flow-control credits, credit status and FCU thresholds, port lane status, posted/non-posted/completion flow-control credit registers, error control, RX control, expected sequence number, RX vendor-specific data/status, RX control 3, allocated RX credits, physical and transaction error injection, NAK counters, LTR capture, link-control/training/width/speed/state registers, link-management status/mask/control, strap and L1 PM substate controls, BCH ECC, HPGI, descriptor, and TXCLK perf count control.

The BIFP6 block begins another structurally similar PCIe port instance. This chunk covers BIFP6 reserved/scratch, port control, TX/RX flow-control and request handling, error control, allocated RX credits, physical-layer error injection, and the first half of transaction-layer error-injection shifts through `ERROR_INJECT_TL_UNEXPECTED_CMPLT`. The remaining BIFP6 transaction masks and later BIFP6 link-control/link-management fields fall outside this chunk and must be reconciled by adjacent chunk research.

## Important APIs, Types, And Constants

This file exposes macros rather than C APIs. The externally visible contract is the generated naming convention:

- `BIFP{4,5,6}_<REGISTER>__<FIELD>__SHIFT` gives the least-significant bit position for a field.
- `BIFP{4,5,6}_<REGISTER>__<FIELD>_MASK` gives the unshifted register mask for the same field.
- `BIFP4`, `BIFP5`, and `BIFP6` identify separate PCIe/BIF port instances. Repeated register names intentionally describe separate hardware blocks, not duplicate software symbols.

Important field families in this range include:

- Error injection: physical-layer lane, framing, SKP parity/LFSR, loopback underflow/overflow, deskew, 8b/10b disparity/decode, SKP ordered-set, invalid ordered-set identifier, and bad sync-header injection; transaction-layer flow-control, replay rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion-timeout injection.
- Link control and training: `LC_RESET_LINK`, L0s/L1 inactivity timers, L1/L23 entry/exit behavior, ASPM/PMI interactions, receiver-idle gating, training control state, compliance receive, speed-change initiation, autonomous change/upconfigure disable, hardware link-disable state, and recovery/equalization timing knobs.
- Link width and speed: negotiated/read link width, reconfiguration triggers, renegotiation/upconfiguration support, dynamic lane power state, lane reversal/equalization handling, target link speed, speed-change attempt counters, equalization phase timers, degraded-link handling, Gen2/Gen3 training flags, and EIEOS/EQ behavior.
- Link state and management: six `LC_STATE*` registers for internal state readback, link-management interrupt/status/mask/control fields for hot reset, speed change, link bandwidth notifications, lane-width changes, link-autonomous bandwidth state, link-disable events, and EQ request/complete states.
- Flow control and credits: TX advertised/init credits for posted, non-posted, and completion traffic, credit-consumed/limit/status fields, FCU thresholds, RX allocated credits, and per-class flow-control credit readbacks.
- RX/TX control: requester ID fields, request counters, replay sequence, ACK latency, RX ignore controls for PCIe protocol errors, RCB completion/FLR timeout controls, TPH/PASID-related ignore fields, one-shot NAK generation, and vendor-specific RX data/status.
- Power and low-power behavior: captured LTR thresholds, L1 PM substate timers and entry/exit controls, L1.1/L1.2 enable/status, idle-to-RX turnoff controls, refclk request/ack timing, and strap fields that control link-capability, lane, ASPM, L0s/L1, lane reversal, and clock/power-gating behavior.
- Diagnostics and platform hooks: NAK counters, HPGI request/command/interrupt/status fields, BCH ECC correction/uncorrectable status, hcnt descriptor, and TXCLK performance counter event/count fields.

## Control Flow

This header chunk has no direct control flow. Runtime control flow appears when AMDGPU code includes the header and uses these constants to read, decode, update, or write NBIO registers. Typical use is:

1. Select a register address from `nbio_7_0_offset.h` or `nbio_7_0_smn.h`.
2. Read the register with a helper such as `RREG32_SOC15` or `RREG32_PCIE`, or prepare a value for write.
3. Extract a field with the generated mask/shift, often through `REG_GET_FIELD`.
4. Preserve unrelated bits and update a field with `REG_SET_FIELD`, then write through `WREG32_SOC15` or `WREG32_PCIE`.

The ordering in this file follows the generated hardware register map, not software execution. The repeated BIFP4/BIFP5/BIFP6 sections represent parallel PCIe port instances with similar layout. Code may program one port instance or another depending on ASIC wiring, board configuration, firmware state, virtualization mode, or diagnostics path.

## State And Persistence Behavior

The macros are compile-time constants and do not store state. The state described by the macros lives in NBIO/BIF PCIe hardware registers.

Some described fields are software-controlled configuration state: link reset/training controls, speed-change controls, ASPM and L1/L23 policy, error-reporting disables, RX ignore controls, LTR threshold masks, HPGI command fields, and error-injection enables. Other fields are hardware-observed state: link state readbacks, negotiated link width/speed, NAK counters, credit status, RX expected sequence numbers, captured LTR status, link-management interrupts, BCH ECC status, and HPGI status.

Persistence is controlled by GPU reset, PCIe link reset, BACO/runtime power transitions, suspend/resume, and ASIC power-domain behavior. The header itself provides no save/restore mechanism and does not encode reset values or access semantics. Driver code using these masks must still know whether a field is read-only, write-one-to-clear, sticky until reset, reserved, strap-derived, or safe for read/modify/write.

## Dependencies And Integration Points

This header is included directly by `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Those files combine NBIO 7.0 masks with the sibling generated headers `nbio_7_0_default.h`, `nbio_7_0_offset.h`, and `nbio_7_0_smn.h`.

Observed integration patterns in nearby code include:

- `nbio_v7_0.c` uses NBIO masks to decode strap fields, configure memory-controller access, doorbell ranges, interrupt behavior, medium-grain clock gating/light sleep, and NBIO register initialization.
- `soc15.c` includes this header as part of the SOC15 ASIC support layer and uses related PCIe register masks to program/read PCIe performance counters and replay/NAK counts.
- Register field helpers (`REG_GET_FIELD`, `REG_SET_FIELD`, `WREG32_FIELD15`) depend on the generated `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` names matching the helper's token-pasting expectations.
- Linux PCIe integration depends indirectly on these definitions through AMDGPU's link training, power management, AER/diagnostic, reset, interrupt, and performance telemetry paths.

The BIFP port fields align with PCI Express concepts: transaction/data-link/physical layer errors, ASPM and L1 substate power management, LTR, link equalization and speed changes, flow-control credits, NAK/replay accounting, hot reset, link-bandwidth management, and vendor-specific port diagnostics.

## Risks And Edge Cases

Generated-register drift is the primary risk. If a single shift or mask differs from the NBIO 7.0 register database, code may silently program the wrong bit, clear a reserved bit, fail to train or retrain the PCIe link, suppress or inject the wrong error, misread link status, or corrupt flow-control settings. Because BIFP4/BIFP5/BIFP6 blocks are intentionally repetitive, accidental template or copy/paste drift can be difficult to distinguish from an intended per-port exception.

Read/modify/write safety is a major concern. Many registers combine software controls, hardware status, reserved fields, sticky status, and write-one-to-clear bits. Mask constants alone do not indicate access type. Code that writes a full value instead of preserving unrelated bits can disturb link training, power-management policy, error reporting, or flow-control credit accounting.

Error-injection fields are especially sensitive. The physical and transaction injection registers can intentionally create protocol errors that may trigger AER, link recovery, replay storms, device reset, or system-level PCIe error handling. Test or debug code must be tightly gated and must avoid leaving injection bits set across reset or resume paths.

Power-management fields are platform-sensitive. LTR thresholds, ASPM/L1/L1.1/L1.2 controls, refclk request timing, receiver standby, and lane power-state controls can affect idle power, wake latency, hotplug behavior, and link stability. Changes should be validated on real hardware across multiple root complexes and firmware configurations.

Chunk boundaries are meaningful. This range starts after the BIFP4 physical error-injection shifts and most masks have already begun in the previous chunk, and it ends before BIFP6 transaction error-injection masks and the rest of BIFP6 link-management fields. The final per-file report should merge adjacent chunks before claiming complete coverage of BIFP4 or BIFP6.

## Test Signals

There are no unit tests for these generated macros in this header. Useful validation signals are build, static comparison, and hardware behavior:

- Build AMDGPU/SOC15/NBIO 7.0 code to catch missing, renamed, or malformed generated macro symbols and helper token-pasting failures.
- Compare the generated header against the authoritative AMD NBIO 7.0 register database or regeneration output, with special focus on repeated BIFP4/BIFP5/BIFP6 symmetry and intentional per-port exceptions.
- Run PCIe link bring-up, retraining, speed-change, hot-reset, suspend/resume, runtime power management, and BACO scenarios on NBIO 7.0 hardware; watch for link-width/speed regressions, training timeouts, ASPM instability, and AMDGPU reset messages.
- Use PCIe/AER diagnostics or controlled validation-only error injection to confirm physical and transaction error bits map to expected hardware behavior and are cleared/restored safely.
- Check replay/NAK counters, PCIe performance counters, link-management status/mask behavior, and debug register dumps against expected values during heavy DMA, graphics, SDMA, video, and KFD queue workloads.
- Validate LTR and L1 substate behavior with platform power-management tooling; failures may appear as elevated idle power, wake latency problems, or intermittent link recovery events.

### subset-b-003098: lines 73205-75613

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 73205-75613

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,170 `#define` field-layout macros and 231 register/address-block comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts in the middle of `BIFP6_PCIEP_ERROR_INJECT_TRANSACTION`, after the first transaction-layer error-injection shift fields are defined in the preceding lines. It then covers PCIe link-controller, PCIe0 directory, performance-counter, PRBS, software-reset, RSMU/SMU, link-counter, NB configuration, SMN-index/data, and IOMMU-shadow field definitions. The chunk ends after `SHADOW_IOMMU_CAP_BASE_HI`; the next source lines begin `nbio_iohub_nb_PCIE0shadow0_pcieshadow_cfgdecp`.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMDGPU's generated NBIO 7.0 register interface. For each hardware register field, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position used when encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`, the register mask used to isolate, clear, preserve, or update the field.

This slice describes PCIe link-management and NBIO control state rather than filesystem behavior, despite living under the repository's Ceph-client source mirror. It gives AMDGPU code symbolic access to low-level PCIe/NBIO hardware fields for link training, link width and speed changes, ASPM/L1 substates, link-management interrupts, error injection, performance counters, PRBS diagnostics, software reset sequencing, SMU/RSMU coordination, NB config-space windows, and IOMMU capability shadowing.

## Important Macro Families

The opening `BIFP6_*` section covers PCIe port and link-controller fields. It includes transaction-layer error-injection masks for flow-control errors, replay-number rollover, bad DLLP/TLP, unsupported request, ECRC, malformed TLP, unexpected completion, completer abort, and completion timeout. It also defines NAK counters, captured LTR interrupt/threshold state, broad `LC_*` controls for link reset, L0s/L1/L23 entry and exit timing, training state, link width renegotiation, N_FTS, speed changes, equalization, lane control, bandwidth-change interrupt status/masks, CDR controls, L1 PM substates, strap fields, BCH ECC, HPGI, and host-controller descriptor/performance counter state.

The `addressBlock: nbio_pcie0_pciedir` section describes the PCIE0 directory register layout. It includes general `PCIE_CNTL` and `PCIE_CONFIG_CNTL` fields, TX tracking address/control fields, bandwidth-by-unit-ID state, RX/TX attributes, CI and bus controls, additional link-controller state/status registers, write-protect control, captured last-RX/TX TLP dwords, I2C register-data expansion, PCIe config control, link power-management controls, port-order controls, port-buffer and decoder status, L0s FTS detection, RX AD controls, SDP/SWUS/RC slave attributes, and `NBIO_CLKREQb_MAP_CNTL`.

The same PCIE0 directory block also contains observability and validation facilities. `PCIE_PERF_CNTL_*` and `PCIE_PERF_COUNT*_*` define event selectors and 32-bit counters for TXCLK, master read/complete clocks, slave read/complete clocks, non-snoop complete clocks, and additional TXCLK lanes. `PCIE_PERF_CNTL_EVENT0_PORT_SEL` and `PCIE_PERF_CNTL_EVENT1_PORT_SEL` select per-clock-domain ports. `PCIE_PRBS_*` defines PRBS clear/status/freerun/misc/user-pattern registers, bit counters, and per-lane error counters 0 through 15.

The reset and management section covers `SWRST_*`, `CPM_CONTROL`, `SMN_APERTURE_ID_*`, `RSMU_*`, `LNCNT_*`, and SMU/HP registers. These fields model software-triggered upstream/downstream link resets, endpoint reset controls, wait-for-linkup behavior, hot-reset/link-disable/link-down reset type selection, reset hold/release enables, clock/power management control, SMN aperture identifiers for SMU/PCS/IOHUB/NBIF, RSMU master/slave/power-gating and BIOS-timer controls, link-counter windows/weights/thresholds/accumulators, SMU hotplug status and command-update handshakes, end-of-interrupt state, interrupt-pin sharing indicators for link management and LTR, and PCIe master/slave power-gating hysteresis.

The `addressBlock: nbio_iohub_nb_nbcfg_nb_cfgdec` section defines northbridge PCI configuration fields. It includes standard identity and header fields (`VENDOR_ID`, `DEVICE_ID`, command, status, revision, class/subclass, cache line, latency, header type, subsystem IDs, and capability pointer), PCI control bits (`PMEDis`, `SErrDis`, `MMIOEnable`, `HPDis`), PCI arbiter/PME/VGA-hole state, DRAM slot base/top-of-DRAM fields, scratch registers, SMN index-extension/index/data windows 0 through 6, index-data mutexes, and a global NB performance-counter control register with enable, shadow-write, reset, and delayed reset/shadow timing fields.

The final `addressBlock: nbio_iohub_nb_iommushadow_iommushadow_cfgdecp` fragment defines the IOMMU shadow capability base. It contains `SHADOW_IOMMU_MMIO_CNTRL_0__IOMMU_EN`, `SHADOW_IOMMU_CAP_BASE_LO__IOMMU_ENABLE`, low base-address bits starting at bit 19, and the high 32 bits of the IOMMU base address.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped C preprocessor integer literals, mostly with an `L` suffix.

Consumers combine these definitions with sibling generated address/default headers and AMDGPU register helpers. Typical users read a hardware register, extract a field with `*_MASK` and `*_SHIFT`, or perform a read/modify/write that clears a field mask and ORs in `(value << shift) & mask`. These macros do not encode register addresses, access permissions, reset values, write-one-to-clear semantics, reserved-bit policy, firmware ownership, or required timing between writes.

## Control Flow

This header has no local runtime control flow. Runtime flow is external and hardware-driven:

1. AMDGPU code selects an NBIO/PCIe/NB configuration register address from companion generated metadata.
2. It reads the register through an MMIO, SMN, PCI config, or indirect-index path appropriate for the register block.
3. It decodes status fields or composes a new register value using the shift/mask constants in this chunk.
4. Hardware state machines then perform link training, link-speed changes, width renegotiation, L1/L23 transitions, reset sequencing, PRBS counting, power gating, or SMU/RSMU handshakes.

The field names imply several asynchronous hardware flows that call sites must sequence and poll carefully: LTSSM/link-controller training state, ASPM and L1-substate entry/exit, receiver idle and electrical-idle detection, speed-change/equalization, CDR behavior, hot reset and link disable, PRBS measurement windows, performance-counter latching, LTR interrupt reporting, power-gating idleness, and IOMMU shadow-base exposure.

## State And Persistence Behavior

The header owns no mutable software state and persists nothing. It describes hardware-visible state in NBIO 7.0 PCIe, RSMU/SMU, NB config, and IOMMU-shadow registers.

Represented state includes writable control bits, strap-derived configuration, counters, interrupt masks/status bits, latched last-TLP captures, error-injection controls, diagnostic selectors, reset commands, reset status, power-gating knobs, SMN index/data windows, scratch registers, DRAM aperture fields, and IOMMU capability-base fields. Some fields are live hardware status (`LC_STATE*`, `LC_STATUS*`, decoder/buffer status, PRBS status, RSMU/SMU status, counter accumulators), while others are configuration or command inputs.

Persistence depends on the ASIC reset domain, PCIe hot/cold reset, NBIO reset, power gating, firmware/BIOS initialization, suspend/resume restore, and explicit AMDGPU writes. The shift/mask macros do not say which fields survive resets, which fields are sticky, or which fields clear on read/write; that must come from the hardware specification and sibling generated default/access metadata.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must stay synchronized with sibling headers such as NBIO 7.0 offset, SMN, and default-value headers. Address metadata names the registers; this file only names the fields inside those registers.

Integration points in AMDGPU include NBIO initialization, PCIe link bring-up and recovery, ASPM/runtime power-management policy, GPU reset and hot-reset handling, interrupt routing and masking, performance/debug tooling, PRBS/link-quality diagnostics, SMU/RSMU mailbox or handshake paths, SMN indirect access through NB config windows, and IOMMU capability/shadow setup. Because many fields mirror standard PCIe concepts, code using them also intersects with the Linux PCI core, PCIe AER/link management, MSI/MSI-X setup elsewhere in the device, power management, and platform firmware configuration.

The SMN index/data definitions are especially sensitive integration points because they describe indirect access windows and mutex bits. Any caller using those windows must coordinate ownership and preserve the unlock/mutex protocol rather than treating index/data writes as independent ordinary registers.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while programming the wrong hardware bit, causing link-training failures, incorrect speed/width negotiation, broken ASPM/L1-substate behavior, missed interrupts, bad reset sequencing, or misleading diagnostics.
- This range starts and ends on chunk boundaries that split logical groups. `BIFP6_PCIEP_ERROR_INJECT_TRANSACTION` begins before line 73205, and the next PCIe shadow address block begins after line 75613. Whole-file research must reconcile those adjacent chunks before treating either boundary group as complete.
- Link-controller fields are timing- and state-machine-sensitive. Writes that reset links, force speed changes, alter equalization, change FTS counts, or override lane controls need ordering, timeouts, and recovery paths.
- Status, mask, and control registers often share similar bit names. Accidentally using a status mask against a control register, or vice versa, can silently change semantics because the constants have compatible integer types.
- Full-width masks such as `0xFFFFFFFFL` appear for captured TLP dwords, counters, scratch registers, SMN index/data windows, and IOMMU high-base fields. Writers still need to respect ownership and side effects; a full mask is not permission for arbitrary writes.
- PRBS, error injection, captured TLP, performance counter, and debug mux fields are diagnostic surfaces. Leaving them enabled or misconfigured can perturb normal PCIe operation or produce confusing telemetry.
- SMN index/data windows and index-data mutex fields are shared access paths. Missing locking, stale indexes, or failure to release/unlock can corrupt unrelated register accesses.
- Power-gating and RSMU/SMU handshake fields can race with runtime PM, suspend/resume, firmware ownership, and GPU reset flows.
- IOMMU shadow enable/base fields affect how the device exposes or mirrors IOMMU capability information. Incorrect base or enable values can break platform enumeration or DMA-remapping expectations.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing, renamed, or malformed generated symbols referenced by consumers.
- Run generated-header consistency checks: each field should have a coherent `__SHIFT`/`_MASK` pair, masks within a register should not overlap unexpectedly, reserved gaps should match the source register database, and repeated performance-counter or PRBS lane definitions should follow the expected pattern.
- Cross-check this shift/mask segment against sibling NBIO 7.0 address/default headers so every register comment in this chunk maps to a known address and reset/default value.
- On supported hardware, validate cold boot, warm reset, GPU reset, suspend/resume, PCIe link retrain, speed changes, width negotiation, ASPM/L1-substate behavior, and hot-reset/link-disable recovery.
- Exercise diagnostics where available: PRBS bit/error counters, performance counters across all listed clock domains, link-management/LTR interrupt status and masks, NAK counters, captured last-TLP registers, and transaction-layer error injection.
- Trace register writes in reset and power-management paths to verify reserved bits are preserved, status bits are cleared according to their documented access type, and SMN index/data mutex ownership is acquired and released correctly.
- Validate IOMMU shadow values during PCI enumeration or platform bring-up by comparing the decoded enable and base-address fields against expected firmware and IOMMU capability placement.

### subset-b-003099: lines 75614-78264

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 75614-78264

## Scope

This chunk is a macro-only section of the AMD NBIO 7.0 register mask header. It defines `__SHIFT` and `__MASK` constants for PCIe shadow bridge configuration, IOHC miscellaneous/fast-register control, trap/debug capture, bridge decode/QoS policy, and the beginning of IOHC SION scheduling/credit tables. There are no C functions, structs, enums, storage objects, or executable control-flow constructs in this slice; its API surface is the exported preprocessor symbol set consumed by lower-level AMDGPU register access code.

## Purpose

The constants in this range describe bitfield layouts for 32-bit NBIO/IOHC registers. Driver code can combine these masks with ASIC register addresses from companion `*_offset.h` headers and reset values from `*_default.h` headers to compose writes, decode reads, and preserve reserved bits. The chunk covers:

- `NB_PCIE0SHADOW0_*` through `NB_PCIE0SHADOW6_*` PCIe type-1 bridge shadow fields.
- Address blocks for `nbio_iohub_nb_NBIF1shadow0_pcieshadow_cfgdecp` and `nbio_iohub_nb_NBIF1shadow1_pcieshadow_cfgdecp`, followed by the fastreg and misc IOHC decode areas.
- IOHC clock gating, performance counters, programmable PCI bridge device/function remaps, interrupt/NMI/SMI/SCI controls, DMA dropped logs, VDM, stall controls, MMIO aperture base/lock controls, power gating, SDP/parity controls, scratch/status, trap request/response state, and `TRAP0` through `TRAP15` comparator programming fields.
- Southbridge-style `SB_*` bridge shadow masks, IOHC decode override masks, QoS priority masks, USB QoS masks, and SION client arbitration/credit fields through `IOHC_SION_S0_Client4_WrRsp_TimeSlot_Lower`.

## Important Macro Families

### PCIe Shadow Bridge Masks

Each `NB_PCIE0SHADOWn_*` group for shadows 0-6 repeats the same bridge register schema:

- `COMMAND`: `IO_ACCESS_EN`, `MEM_ACCESS_EN`, `BUS_MASTER_EN`.
- `SUB_BUS_NUMBER_LATENCY`: secondary and subordinate bus number fields.
- `IO_BASE_LIMIT`, `IO_BASE_LIMIT_HI`: split I/O window base/limit fields.
- `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`: memory and prefetchable memory bridge windows.
- `IRQ_BRIDGE_CNTL`, `EXT_BRIDGE_CNTL`, `PMI_STATUS_CNTL`, `SLOT_CAP`, `ROOT_CNTL`, `DEVICE_CNTL2`: bridge legacy decode, port 0x80 routing, power state, slot power, CRS visibility, and ARI forwarding fields.

These macros are integration points for PCIe topology setup, GPU bridge enumeration, reset restore paths, and any platform-specific bridge resource programming. The fields mirror PCI/PCIe configuration space semantics, but live in NBIO shadow decode space.

### IOHC Fastreg and Miscellaneous Controls

The fastreg/misc section defines masks for IOHC mode and policy registers:

- `IOHC_REFCLK_MODE`, `IOHC_PCIE_CRS_Count`, `IOHC_P2P_CNTL`, `IOHC_AER_CNTL`, and `SB_LOCATION` expose reference clock, CRS retry timing, peer-to-peer behavior, AER behavior, and southbridge location metadata.
- `IOHC_GLUE_CG_LCLK_CTRL_0/1/2` soft override fields cover many local clock lanes. These are hardware power/clock controls; incorrect writes can prevent expected clock gating or force clocks on.
- `IOHC_PERF_CNTL` selects four performance events, with `IOHC_PERF_COUNT0..3` and `*_UPPER` exposing 56-bit-style counter values split across lower 32-bit and upper 24-bit fields.
- `NB_PROG_DEVICE_REMAP_PBr0..PBr8` maps PCI bridge device/function identifiers.
- `SW_NMI_CNTL`, `SW_SMI_CNTL`, `SW_SCI_CNTL`, `SW_GIC_SPI_CNTL`, `IOHC_INTERRUPT_EOI`, `SW_SYNCFLOOD_CNTL`, `IOHC_PIN_CNTL`, and `IOHC_INTR_CNTL` define software interrupt, end-of-interrupt, sync flood, pin mode, and destination controls.
- `IOHC_FEATURE_CNTL` and `IOHC_FEATURE_CNTL2` expose P2P mode, architecture/ARI/dGPU feature bits and status bits such as NMI, SERR, CRS, and posted/non-posted DMA dropped status.
- `NB_TOP_OF_DRAM3` and `NB_DRAM3_BASE` describe high DRAM decode ranges.
- `PSP_BASE_ADDR_*`, `SMU_BASE_ADDR_*`, `IOAPIC_BASE_ADDR_*`, `FASTREG_BASE_ADDR_*`, `FASTREGCNTL_BASE_ADDR_*`, and `SMMU_BASE_ADDR_*` encode MMIO aperture enables, lock bits, and base address fields for security, firmware, interrupt, fast register, and SMMU blocks.
- `IOHC_PGMST_CNTL`, `IOHC_SDP_PORT_CONTROL`, `IOHC_SDP_PARITY_CONTROL`, and `IOHC_PGSLV_CNTL` define power-gating/idleness and SDP parity behavior.
- `SCRATCH_4`, `SCRATCH_5`, `SMU_BLOCK_CPU`, and `SMU_BLOCK_CPU_STATUS` provide firmware/driver scratch and SMU CPU-block handshake/status fields.

### CAM, DMA Dropped Logs, VDM, and Stall Controls

`CAM_CONTROL` plus `CAM_TARGET_*` fields configure a content/address match mechanism with enable, operation, access type, data-match, VC, and cross-trigger controls. The DMA dropped log families (`P_DMA_DROPPED_LOG_LOWER/UPPER` and `NP_DMA_DROPPED_LOG_LOWER/UPPER`) expose one mask bit per logged source/slot across lower and upper words. `PCIE_VDM_NODE0_CTRL4`, `PCIE_VDM_CNTL2`, and `PCIE_VDM_CNTL3` provide VDM routing and SMU/MCTP/APMTP master controls. `STALL_CONTROL_XBARPORT*_0/1` fields allow request/response stalling per virtual channel for crossbar ports, which is useful for debug but risky for normal traffic.

### Trap Request, Response, and Comparator Programming

The trap infrastructure has two layers:

- Global trap request/response capture: `TRAP_STATUS`, `TRAP_REQUEST0..5`, `TRAP_REQUEST_DATASTRB0/1`, `TRAP_REQUEST_DATA0..15`, `TRAP_RESPONSE_CONTROL`, `TRAP_RESPONSE0`, and `TRAP_RESPONSE_DATA0..15` describe a captured request address, command, attributes, length, VC, security level, data/parity, response status, and response payload.
- Sixteen trap comparators: `TRAP0_*` through `TRAP15_*` repeat the same pattern of `CONTROL0`, `ADDRESS_LO`, `ADDRESS_HI`, `COMMAND`, `ADDRESS_LO_MASK`, `ADDRESS_HI_MASK`, and `COMMAND_MASK`. Each control register has enable, SMU interrupt, and cross-trigger fields. Address low fields start at bit 2, matching dword alignment.

This block is a debug and error-observation interface. Driver consumers should program trap enables and masks carefully because overly broad comparators can generate interrupt/debug traffic or stall diagnosis paths.

### Decode, SB Bridge, QoS, and SION Scheduling

The decode override registers (`IOHC_REQDECODE_OVERRIDE`, `IOHC_RSPDECODE_OVERRIDE`, and `IOHC_RSPPASSPW_OVERRIDE`) allocate four bits per client 0-7. `IOHC_USERBIT_BYPASS`, `IOHC_SMN_MASTER_CNTL`, and `IOHC_SMN_MASTER_STATUS` control user-bit bypass and SMN error/poison status mapping.

`SB_*` repeats the PCIe bridge schema for southbridge shadow configuration: command bits, bus numbers, I/O and memory windows, IRQ/VGA/ISA decode, port 0x80, power state, slot power, CRS, and ARI forwarding.

`IOHC_QOS_CONTROL` assigns four-bit QoS priority fields to VC0-VC7, while `USB_QoS_CNTL` carries unit IDs, priority, and enable fields for two USB units.

The SION block begins a large table of 32-bit full-word masks for per-client arbitration and credit programming. For clients 0-3, this chunk includes S0 and S1 request, read-response, and write-response `BurstTarget` and `TimeSlot` lower/upper words plus request/data/read-response/write-response pool credit allocation lower/upper words. Client 4 begins in this chunk and continues into the next chunk, ending here at `IOHC_SION_S0_Client4_WrRsp_TimeSlot_Lower`.

## Control Flow and State Behavior

There is no runtime control flow in this header. State changes happen only when consumers use these masks to read or write hardware registers. The state represented here is persistent hardware-visible state until reset, power-gated domain loss, firmware reprogramming, or explicit driver writes. Notable state categories include:

- PCI bridge resource windows and enable bits that affect config-space decode and DMA reachability.
- Interrupt, NMI/SMI/SCI, sync flood, and EOI state that can affect platform signaling.
- MMIO base/enable/lock fields for PSP, SMU, IOAPIC, fastreg, fastreg control, and SMMU apertures. Lock fields are especially sensitive because writes may become irreversible until reset.
- Debug/trap/CAM/stall state that can capture, reroute, or block traffic.
- QoS and SION scheduling/credit state that changes ordering, bandwidth share, and backpressure behavior for IOHC clients.

## Dependencies and Integration Points

This file depends on the C preprocessor only. It is intended to be included by AMDGPU/NBIO code alongside related generated headers:

- `nbio_7_0_offset.h` for register addresses.
- `nbio_7_0_default.h` for reset/default values.
- AMDGPU register helpers that apply `MASK`, `SHIFT`, `REG_SET_FIELD`, or equivalent bitfield utilities.

The constants integrate with Linux DRM AMDGPU PCIe/NBIO initialization, suspend/resume restore, reset handling, debugfs or diagnostics that expose performance/trap/error state, firmware-mediated SMU/PSP control paths, and platform-specific bridge or MMIO aperture setup.

## Risks

- Because this is generated hardware documentation as C macros, a single wrong mask or shift silently corrupts unrelated bits in hardware register writes.
- Many fields share repeated schemas. Copy/paste or generation mistakes are hard to detect by inspection, especially across `NB_PCIE0SHADOW0..6`, `TRAP0..15`, dropped-log bit arrays, and SION client tables.
- Lock bits in MMIO base registers can make bad base/enable programming persist until reset.
- Trap, CAM, and stall controls can perturb live traffic if debug code enables broad matches or stalls production virtual channels.
- QoS and SION credit fields are full-width table entries; invalid scheduling or credit values can create starvation, latency spikes, or deadlock-like backpressure.
- This chunk ends in the middle of the client 4 SION block, so downstream reconciliation must merge with the next chunk before treating the SION table as complete.

## Test and Validation Signals

- Build-time validation: compile AMDGPU code that includes `nbio_7_0_sh_mask.h`; undefined or duplicate macro failures would catch gross header breakage.
- Static consistency checks: verify every `__MASK` aligns with its `__SHIFT`, especially repeated one-bit fields, address low fields shifted by 2, upper 24-bit performance counters, and four-bit-per-client decode/QoS fields.
- Cross-header checks: compare symbol stems against `nbio_7_0_offset.h` register names and `nbio_7_0_default.h` defaults for the same NBIO generation.
- Runtime smoke signals: successful PCIe bridge enumeration, preserved BAR/resource windows after suspend/resume, no unexpected NMI/SMI/SCI or AER/CRS status changes, and stable PSP/SMU/SMMU/IOAPIC MMIO access.
- Debug validation: trap/CAM programming should capture expected requests only; performance counters should increment for selected events; SION/QoS changes should be tested with traffic stress and checked for hangs, dropped DMA status bits, or performance regressions.

### subset-b-003100: lines 78265-80596

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 78265-80596

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.0 shift/mask header. It defines preprocessor constants for bit positions and masks in NBIO IO hub registers, primarily the `nbio_iohub_nb_rascfg_ras_cfgdec` RAS configuration address block and the beginning of the `nbio_iohub_nb_psprascfg_pspras_cfgdec` PSP-facing RAS status block.

The first few lines complete the preceding IOHC SION traffic-management area for client 4: S0/S1 write-response time slots, S1 request/read-response/write-response burst targets and time slots, request/data/read-response/write-response pool-credit allocation dwords, and a live-lock watchdog threshold. The main body then defines parity, global RAS, PCIe/NBIF action, sync-flood, poison, APML, and PSP status fields.

This is hardware metadata, not executable driver logic. AMDGPU register access helpers consume these constants with companion offset/SMN/default headers so C code can encode and decode individual hardware fields without embedding literal bit positions.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this range. The public interface is the generated macro pattern:

- `<REGISTER>__<FIELD>__SHIFT`: the field's starting bit.
- `<REGISTER>__<FIELD>_MASK`: the field mask already shifted into register position.

Major register families in this chunk are:

- `IOHC_SION_*Client4*` and `IOHC_SION_LiveLock_WatchDog_Threshold`: 32-bit lower/upper masks for SION client 4 request, read-response, and write-response burst/time-slot scheduling, plus pool-credit allocation dwords for request, data, read-response, and write-response pools. These fields are full-width dwords except the watchdog threshold, which uses bits 7:0.
- `PARITY_CONTROL_0` and `PARITY_CONTROL_1`: parity corrected/UCP thresholds and parity error-injection selectors. `PARITY_CONTROL_1` selects group, group type, ID, command, trigger, and injection-allow bits.
- `PARITY_SEVERITY_CONTROL_UNCORR_0`, `PARITY_SEVERITY_CONTROL_CORR_0`, and `PARITY_SEVERITY_CONTROL_UCP_0`: two-bit severity selectors for parity groups 0-4, split by uncorrectable, correctable, and UCP classes.
- `RAS_GLOBAL_STATUS_LO` and `RAS_GLOBAL_STATUS_HI`: top-level RAS status bits. The low dword reports parity classes, HPLGWA interrupt classes, software SMI/SCI/NMI, APML NMI/sync-flood status, pin sync-flood NMI, and private APML sync-flood. The high dword reports PCIE0 ports A-G and NBIF1 ports A-B error sources.
- `PARITY_ERROR_STATUS_UNCORR_GRP[0-4]`, `PARITY_ERROR_STATUS_CORR_GRP[0-4]`, and `PARITY_ERROR_STATUS_UCP_GRP[0-4]`: per-ID status bitmaps, 32 IDs per group, for each parity class.
- `PARITY_COUNTER_CORR_GRP[0-4]` and `PARITY_COUNTER_UCP_GRP[0-4]`: 16-bit per-group counters for correctable and UCP parity errors.
- `MISC_SEVERITY_CONTROL` and `MISC_RAS_CONTROL`: severity for miscellaneous event and PCIe parity errors, plus global RAS output controls and enables for pin NMI sync flood, GNB sideband link disable behavior, interrupt/link-disable/sync-flood output suppression, PCIe NMI/SCI/SMI, and software SCI/SMI/NMI.
- `RAS_SCRATCH_0` and `RAS_SCRATCH_1`: full-width software scratch fields.
- `*_ACTION_CONTROL`: a repeated action-control schema for error classes. Each register exposes `APML_ERR_En`, two-bit `IntrGenSel`, `LinkDis_En`, and `SyncFlood_En`. This chunk covers generic error event and parity classes, PCIE0 ports A-G SERR/internal fatal/internal nonfatal/internal corrected/external fatal/external nonfatal/external corrected/parity-error actions, and NBIF1 ports A-B with the same subevents.
- `SYNCFLOOD_STATUS` and `NMI_STATUS`: source status for sync-flood and pin NMI events. Sync-flood status includes RAS control, APML, pin, private, and IOHC port bits 8-31.
- `POISON_ACTION_CONTROL`: action routing for internal poison, low-side egress poison, and high-side egress poison. Each category repeats APML error enable, interrupt-generation selection, link-disable enable, and sync-flood enable fields.
- `INTERNAL_POISON_STATUS`, `INTERNAL_POISON_MASK`, `EGRESS_POISON_STATUS_LO`, `EGRESS_POISON_STATUS_HI`, `EGRESS_POISON_MASK_LO`, `EGRESS_POISON_MASK_HI`, `EGRESS_POISON_SEVERITY_DOWN`, and `EGRESS_POISON_SEVERITY_UPPER`: internal and egress poison source bitmaps, masks, and severity bitmaps.
- `APML_STATUS`, `APML_CONTROL`, and `APML_TRIGGER`: APML-facing corrected/nonfatal/fatal/SERR/poison status, NMI and sync-flood enable controls, output-disable control, and software NMI trigger bit.
- `PSP_SYNCFLOOD_STATUS`, `PSP_INTERNAL_POISON_STATUS`, and the start of `PSP_EGRESS_POISON_STATUS_LO`: PSP-visible mirrors for sync-flood and poison sources. This chunk includes all PSP sync-flood source bits, all PSP internal poison bits 0-7, and the `PSP_EGRESS_POISON_STATUS_LO` shifts for bits 0-31 plus masks through bit 27.

These macros are expected to be used through AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, and the SOC15/NBIO register read-write wrappers. Register addresses come from the matching NBIO 7.0 offset or SMN headers; this file only supplies field geometry.

## Control Flow and Runtime Behavior

This chunk has no runtime control flow. It is included at compile time and contributes constants to read-modify-write operations in NBIO, PCIe, RAS, poison-handling, interrupt-routing, APML, and PSP integration code.

The implied hardware flows are:

1. IOHC SION client-4 scheduling and pool-credit registers shape request, data, read-response, and write-response arbitration. The lower/upper fields indicate 64-bit-style split programming surfaces stored as pairs of 32-bit registers.
2. Parity RAS setup writes threshold, severity, and error-injection fields before hardware detects or injects parity events. Status registers then expose per-group/per-ID latches for uncorrectable, correctable, and UCP classes, and counters accumulate selected corrected/UCP events.
3. Global RAS status aggregates individual parity, PCIe port, NBIF port, software, APML, and pin-originated events into low/high status dwords. Driver code can use these masks to classify an event source before reading lower-level status registers.
4. Action-control registers map each RAS event class to externally visible consequences: APML error reporting, an interrupt generation class, link disable, and sync flood. The same four-field schema appears for generic parity events and each PCIE0/NBIF1 port subevent.
5. Sync-flood, NMI, and poison status registers provide source bitmaps that firmware, RAS code, or debug code can read after a fatal path, link-disabling path, APML notification, or poison propagation.
6. APML control/status/trigger fields expose RAS events to platform management and can also trigger APML NMI behavior when enabled.
7. The PSP RAS block mirrors selected sync-flood and poison information for the Platform Security Processor's view of the same IO hub events.

All side effects are in the hardware registers that callers access. The header does not sequence operations, clear status bits, or enforce ordering; the driver and firmware-facing code must apply any required status-clear, mask-before-enable, or trigger-after-programming ordering.

## State and Persistence

The header owns no state, allocates no memory, performs no I/O, and persists nothing. The represented state is in NBIO 7.0 hardware registers.

State categories represented here include:

- Scheduler and credit configuration for IOHC SION client 4, including full-width burst-target/time-slot and pool-credit dwords plus an 8-bit live-lock watchdog threshold.
- RAS policy state: parity thresholds, error-injection selectors, parity severity controls, miscellaneous severity controls, global RAS output suppression, PCIe/software interrupt enables, APML output control, and per-event action routing.
- RAS observation state: global status low/high dwords, parity status bitmaps, corrected/UCP parity counters, sync-flood and NMI source status, poison source status, APML status, and PSP-visible sync-flood/poison mirrors.
- Scratch state in `RAS_SCRATCH_0` and `RAS_SCRATCH_1`, which are full 32-bit fields intended for software/firmware coordination or diagnostics.
- Mask and severity state for poison events, including internal poison masking and egress poison low/high masks and severity bitmaps.

Persistence across GPU reset, PCI reset, suspend/resume, BACO, or runtime power transitions is not specified by this header. Those semantics are defined by NBIO hardware behavior and any driver reinitialization that uses these constants after a reset or power-state transition.

## Dependencies and Integration Points

Primary dependencies are the adjacent generated NBIO 7.0 headers:

- `nbio_7_0_offset.h` for MMIO/config-space register offsets corresponding to these register names.
- `nbio_7_0_smn.h` for SMN-addressed NBIO registers.
- `nbio_7_0_default.h` for reset/default values.
- Adjacent chunks of `nbio_7_0_sh_mask.h`: the previous chunk owns the start of the IOHC SION client-4 section, and the next chunk completes `PSP_EGRESS_POISON_STATUS_LO`.

Likely integration areas in the AMDGPU tree include:

- NBIO 7.0 setup and low-level register access in `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`.
- SOC15-era initialization paths that include NBIO generated metadata.
- AMDGPU RAS handling that classifies parity, poison, PCIe, NBIF, sync-flood, fatal, nonfatal, corrected, and SERR events.
- Platform management paths that expose events through APML NMI/sync-flood mechanisms.
- PSP/firmware coordination paths that read PSP-facing sync-flood and poison mirrors.
- PCIe/NBIO link and error-reporting paths where action-control bits can generate interrupts, request link disable, or propagate sync flood.

Because the file is generated metadata, integration is by symbol naming. A register accessor must pair a `*_SHIFT`/`*_MASK` macro from this file with the matching register address macro from the offset/SMN header and with hardware documentation for field value meanings.

## Risks

- Incorrect masks or shifts can silently program the wrong RAS policy bit or misread the wrong status bit. In this chunk that can affect fatal/nonfatal/corrected event classification, poison handling, APML notification, sync flood, link disable, or interrupt routing.
- Action-control registers are highly repetitive across parity, PCIE0 ports A-G, and NBIF1 ports A-B. A generator or copy/paste error in one port/subevent may be missed if testing exercises only one PCIe port.
- Many status and mask registers have similar names. Confusing `*_STATUS_*` with `*_MASK_*`, or corrected parity groups with UCP/uncorrectable groups, can suppress events or report false events.
- `PARITY_CONTROL_1` exposes error-injection fields, including trigger and injection-allow bits. Misuse by debug or validation code can intentionally create hardware errors outside controlled test paths.
- `MISC_RAS_CONTROL`, APML controls, and action-control fields can disable outputs or enable disruptive actions such as link disable and sync flood. Bad writes can either hide critical errors or escalate recoverable events.
- Poison handling fields are split across internal poison, egress low-side, and egress high-side paths. Using the wrong mask or severity bitmap can misroute poison reporting.
- The chunk boundary is in the middle of the PSP egress poison low-status register: masks for bits 28-31 are not present in this work item and must be taken from the next chunk.
- Full-width SION scheduling and pool-credit fields have no in-header value constraints. Callers need hardware-programming knowledge to avoid starvation, deadlock, or live-lock watchdog behavior.

## Test and Validation Signals

Useful validation signals are generated-header consistency checks plus hardware or emulator coverage:

- Build AMDGPU configurations that include NBIO 7.0 users to catch missing or malformed macro definitions.
- Check that complete registers in lines 78265-80596 have paired `__SHIFT` and `_MASK` definitions, while allowing the intentional split for `PSP_EGRESS_POISON_STATUS_LO` masks 28-31 at the chunk end.
- Cross-check register names against `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, and `nbio_7_0_default.h` so every register with field masks has an address/default definition where expected.
- Run mechanical symmetry checks across repeated action-control registers: generic parity actions, PCIE0 ports A-G, and NBIF1 ports A-B should share the same four field positions (`APML_ERR_En`, `IntrGenSel`, `LinkDis_En`, `SyncFlood_En`).
- Validate parity RAS paths by reading thresholds/severity, injecting controlled parity events through `PARITY_CONTROL_1` where hardware validation permits it, and confirming global status, per-group status, counters, interrupts, APML reporting, and clear behavior.
- Validate poison handling by exercising internal and egress poison reporting and checking the corresponding status, mask, severity, APML, and PSP mirror fields.
- Validate sync-flood and NMI source reporting by checking RAS-control, APML, pin, private, and IOHC port source bits after controlled events.
- Run reset and suspend/resume coverage on NBIO 7.0 ASICs to ensure driver initialization restores RAS policy registers and that status/scratch registers behave according to expected retention semantics.

## Chunk Boundary Notes

This chunk starts mid-IOHC-SION client-4 register family at the `IOHC_SION_S0_Client4_WrRsp_TimeSlot_Lower` field and quickly transitions into the `nbio_iohub_nb_rascfg_ras_cfgdec` address block. It covers that RAS block through `APML_TRIGGER`, then enters `nbio_iohub_nb_psprascfg_pspras_cfgdec`.

The final register in this work item, `PSP_EGRESS_POISON_STATUS_LO`, is incomplete by line range: shifts for bits 0-31 and masks for bits 0-27 are inside this chunk, while masks for bits 28-31 begin in the next chunk at line 80597. Merge/reconciliation should treat that as an artifact of chunking, not a missing-definition defect in the source.

### subset-b-003101: lines 80597-83011

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 80597-83011

## Scope

This chunk covers a generated NBIO 7.0 shift/mask register header segment. It starts in the tail of `PSP_EGRESS_POISON_STATUS_LO` mask definitions, covers the full `PSP_EGRESS_POISON_STATUS_HI` and PSP parity/error-action families, then moves through NB device-indirect configuration blocks, IOMMU and IOAPIC indirect windows, IOMMU L2 PCI/SMMU capability fields, and the beginning of the IOMMU L2 index-control block. The final line is only the `//L2_L2B_MEMPWR_GATE_2` marker; the field definitions for that register begin in the next chunk and are out of scope here.

The file is a generated hardware ABI map. It defines preprocessor constants only: no functions, structs, storage, locking, persistence code, or executable control flow live in this range.

## Purpose

The purpose of this section is to give AMDGPU and related power-management code the bit positions for NBIO 7.0 register fields. Each register field is represented by the usual pair:

- `<REGISTER>__<FIELD>__SHIFT`, the field's bit offset.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to extract or compose the field.

Consumers combine these constants with AMD register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_FIELD15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`. The main local include users for `nbio_7_0_sh_mask.h` are `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. The companion `nbio_7_0_default.h` gives reset defaults for these same logical registers; the NBIO 7.0 offset header uses `cfg...` names for many configuration-space blocks rather than the `reg...` style seen in newer NBIO variants.

## Important Macro Families

### PSP Poison and Parity Status

The opening definitions complete `PSP_EGRESS_POISON_STATUS_LO` and then define all 32 bit positions for `PSP_EGRESS_POISON_STATUS_HI`. Together these expose a 64-bit poison-status bitmap from the Platform Security Processor egress path.

The PSP parity block then defines:

- `PSP_PARITY_CONTROL_0`, with independent 16-bit corrected and uncorrected-parity threshold fields.
- `PSP_PARITY_STATUS`, with summary flags for corrected, non-fatal, fatal, and SERR-class parity errors.
- `PSP_PARITY_ERROR_STATUS_UNCORR_GRP0..4`, `PSP_PARITY_ERROR_STATUS_UCP_GRP0..4`, and `PSP_PARITY_ERROR_STATUS_CORR_GRP0..4`, each exposing 32 one-bit `ParityErrDetected_Id*` fields.
- `PSP_PARITY_COUNTER_UCP_GRP0..4` and `PSP_PARITY_COUNTER_CORR_GRP0..4`, each with a 16-bit `ThresholdCounter` and a high-bit `ResetEn`.
- `PSP_ParitySerr_ACTION_CONTROL`, `PSP_ParityFatal_ACTION_CONTROL`, `PSP_ParityNonFatal_ACTION_CONTROL`, and `PSP_ParityCorr_ACTION_CONTROL`, each exposing `APML_ERR_En`.

The reset defaults in `nbio_7_0_default.h` show zeroed status/counter/action registers and `smnPSP_PARITY_CONTROL_0_DEFAULT` as `0x00010001`, indicating nonzero default thresholds. These masks are therefore relevant to RAS/error reporting paths, even though no in-tree direct consumer of these exact field names was found in the requested search scope.

### NB Device-Indirect Configuration Bridges

The range contains repeated device-indirect configuration blocks for:

- `NB_PCIE0DEVINDCFG0..6`
- `NB_NBIF1DEVINDCFG0..1`
- `NB_INTSBDEVINDCFG0`

Each instance has the same pattern:

- `IOHC_Bridge_CNTL`: disables or policy bits for bridge, bus master, config access, peer-to-peer, VDM, unsupported-request masking, posted-write passing, no-snoop, forced posted-write response, IDO mode, external device plug/CRS handling, CRS enable, APIC enable, and APIC range.
- `IOHC_Bridge_STATUS`: `MaskUR_Status`.
- `STEERING_CNTL`: `ForceSteering` and 8-bit `SteeringValue`.
- `IOHC_Bridge_SCRATCH_0/1`: full-width scratch fields.

These repeated macros model per-port or per-device NB routing and bridge behavior. The default header shows these blocks defaulting to zero. A driver or firmware path that programs these fields is changing low-level PCIe/NBIO routing, config visibility, APIC routing, and unsupported-request behavior for a specific device-indirect target.

### PCIe Dummy Configuration Functions

`NB_PCIEDUMMY0_1_*` and `NB_PCIEDUMMY1_1_*` describe minimal PCI configuration fields for dummy PCIe functions:

- vendor and device ID.
- command and status words.
- class code and revision ID.
- header type and writeable header-type device-type bit.

The defaults show `HEADER_TYPE` values with the device-type bit set and `HEADER_TYPE_W` defaulting to `0x80`. These fields appear intended to expose or emulate dummy config-space endpoints rather than drive normal GPU engines.

### Indirect Register Access Windows

The chunk defines simple full-width index/data windows:

- `IOMMU_SMN_INDEX_0`, `IOMMU_SMN_DATA_0`, `IOMMU_SMN_INDEX_1`, `IOMMU_SMN_DATA_1`.
- `IOAPIC_MIO_INDEX`, `IOAPIC_MIO_DATA`.
- `NB_PCIE0RCBDG_INDCFG0..6_RC_SMN_INDEX/DATA`.
- `NB_NBIF1RCBDG_INDCFG0..1_RC_SMN_INDEX/DATA`.

These macros describe indirect access registers rather than ordinary configuration knobs. Correct control flow for consumers is write-index then read or write data, with any required serialization handled by the calling driver or firmware path. The header itself does not encode sequencing or locking, so callers must avoid interleaving accesses to the same indirect window.

### IOMMU L2 PCI Capability and SMMU Identity

The `IOMMU_L2_1_*` block defines PCI-like configuration fields for the IOMMU L2 function:

- basic PCI identity and command/status fields, including IO, memory, bus-master, parity, SERR, interrupt disable, abort/error, and capability-list bits.
- revision, programming interface, class, cache-line, latency, header, BIST, adapter ID, capabilities pointer, interrupt line/pin, and MSI/MSI mapping fields.
- AMD IOMMU capability fields for cap header, base address low/high, range, miscellaneous capability sizing, guest/GA features, SMMU MMIO enable/lock, and writeable capability controls.
- DSFX/DSSX/DSCX control or dummy status fields.
- L2-to-IOHC poison/stall controls.
- SMMU ID registers: `SMMU_MMIO_IDR0_W`, `IDR1_W`, `IDR2_W`, `IDR3_W`, `IDR5_W`, `IIDR_W`, and `AIDR_W`.

Defaults in `nbio_7_0_default.h` include AMD vendor ID `0x1022`, device ID `0x15d1`, an interrupt pin default of `1`, and nonzero capability/feature defaults such as `IOMMU_MMIO_CONTROL0_W`, `IOMMU_MMIO_CONTROL1_W`, and `SMMU_MMIO_IDR0_W`. These masks are therefore part of the contract through which the hardware advertises IOMMU/SMMU capabilities to platform code.

### IOMMU L2 Index-Control Block

The final part of the chunk enters `nbio_iohub_iommu_l2indx_l2indxcfg` and defines control fields for IOMMU L2 behavior:

- `L2_STATUS_1` and `L2_SB_LOCATION`, exposing L2 status and sideband location fields.
- `L2_CONTROL_5` and `L2_CONTROL_6`, controlling queue arbitration priority, flow-control disables, DTC update policy, forced table-walk behavior, partial PTC control, hysteresis, sequential invalidation burst limits, and performance thresholding.
- `L2_PDC_CONTROL`, `L2_PDC_HASH_CONTROL`, and `L2_PDC_WAY_CONTROL`, configuring the page-directory cache: LRU update priority, parity enable/support, invalidation selection, soft invalidate, search direction, bypass, way/entry counts, address mask, and disabled/access-disabled ways.
- `L2B_UPDATE_FILTER_CNTL`, covering L2B update-filter bypass and read latency.
- `L2_TW_CONTROL`, `L2_TW_CONTROL_1..3`, covering table-walker coherency, prefetch, PTE behavior on untranslated/address-translation excludes, filter disables, parity-error walking behavior, access/AP bit handling, guest prefetch, and debug address controls.
- `L2_CP_CONTROL` and `L2_CP_CONTROL_1`, covering command-processor prefetch disable, flush-on-wait/invalidate, read delay, and L1-off controls.
- `IOMMU_L2_GUEST_ADDR_CNTRL`, defining a 24-bit guest address mask.
- `L2_CREDIT_CONTROL_0/1`, defining flow-control credit counts and override bits for FC, ATS, PDTI, TWEL, CP prefetch, and PPR MCIF paths.
- `L2_ERR_RULE_CONTROL_0..2`, defining rule locks and disable bitmaps.
- `L2_L2B_CK_GATE_CONTROL`, controlling L2B register/dynamic/misc/cache clock gating, gating length, and stop timing.
- `PPR_CONTROL`, controlling page-request interrupt time/request delays and interrupt coalescing.
- `L2_L2B_PGSIZE_CONTROL`, defining guest and host page-size fields.
- `L2_L2B_MEMPWR_GATE_1`, enabling light sleep, deep sleep, shutdown, and memory selection bits for L2B/register/cache power gating.

The default header gives meaningful nonzero reset values for several of these, including `L2_CONTROL_5`, `L2_CONTROL_6`, `L2_PDC_CONTROL`, `L2B_UPDATE_FILTER_CNTL`, `L2_TW_CONTROL`, `L2_CP_CONTROL`, `L2_CREDIT_CONTROL_0/1`, `L2_L2B_CK_GATE_CONTROL`, and `L2_L2B_PGSIZE_CONTROL`. That makes these fields part of hardware initialization state even when the driver never explicitly writes them.

## Control Flow

There is no runtime control flow in this header. Runtime flow is imposed by caller code that reads, modifies, and writes registers. For ordinary fields, the typical pattern is read register, compose a new value with `REG_SET_FIELD` or masks/shifts, then write it back. For status fields, callers read and mask with the relevant `_MASK` constant and shift if needed.

Indirect windows in this chunk require stronger ordering from callers: write an index register such as `IOMMU_SMN_INDEX_*` or `*_RC_SMN_INDEX`, then access the matching data register. The header does not provide mutual exclusion, so any shared indirect window needs caller-side serialization.

Command-like fields also need caller discipline. Examples include `PDCSoftInvalidate`, counter `ResetEn` bits, action-control enables, and debug/table-walker controls. These are not passive metadata fields; writes may trigger hardware state changes, reset counters, alter invalidation behavior, or expose error signaling paths.

## State and Persistence

The macros themselves are compile-time constants and hold no state. The state is in hardware registers:

- PSP poison/parity status and counters persist in device register state until hardware clears them, driver code clears them, or reset occurs.
- NB bridge control, steering, scratch, dummy PCI config, IOMMU capability overrides, and IOMMU L2 controls are device configuration state.
- Indirect index registers are transient cursor state for their matching data ports.
- L2 cache, table-walker, credit, page-size, clock-gating, and power-gating fields directly affect IOMMU runtime behavior while programmed.

The companion default header records reset defaults for the same logical registers, but this chunk does not enforce defaults or restore state across suspend/resume, GPU reset, PCI function reset, or SR-IOV transitions.

## Dependencies and Integration Points

This chunk depends on AMDGPU register-helper conventions and the matching NBIO 7.0 generated headers:

- `nbio_7_0_offset.h` for configuration register offsets, especially `cfg...` definitions.
- `nbio_7_0_default.h` for default values.
- `nbio_7_0_smn.h` for the smaller set of SMN constants used by this NBIO generation.
- SOC15/NBIO access helpers used by `amdgpu/nbio_v7_0.c` and `amdgpu/soc15.c`.
- SMU10 power-management include aggregation through `pm/powerplay/hwmgr/smu10_inc.h`.

Although direct in-tree references to many field names in this exact chunk are sparse, the header is included wholesale for NBIO 7.0 ASIC support. Generated register headers are integration boundaries with firmware tables, hardware programming sequences, RAS handling, IOMMU setup, and platform power-management code.

## Risks

- Wrong masks or shifts silently program the wrong hardware bits. This is especially risky for bridge disable, bus-master/config disable, P2P, APIC routing, IOMMU capability, table-walker, and clock/power-gating fields.
- Indirect index/data windows can race if multiple callers use the same window without serialization.
- Treating status bits as writeable configuration, or configuration bits as harmless status, can clear diagnostics, reset counters, or alter hardware behavior.
- Reserved fields are explicitly represented in several registers. Callers should preserve reserved bits unless hardware documentation says otherwise.
- `L2_PDC_CONTROL`, `L2_TW_CONTROL`, credit controls, and page-size controls can affect address translation correctness and performance. Bad programming may cause DMA/IOMMU faults, stale translations, invalid prefetch behavior, or page-request storms.
- Power and clock-gating fields can create hangs or lost register accesses if changed while the L2 block is active or without the required idle checks.
- The chunk boundary is mid-register-family: `L2_L2B_MEMPWR_GATE_2` is named but its fields are not included here. Research consumers should merge this with the following chunk before making conclusions about the full memory-power-gating family.

## Test Signals

Useful validation signals for changes touching consumers of these macros include:

- Successful build of the AMDGPU driver with NBIO 7.0 support enabled; generated macro names must compile in all included translation units.
- Boot/probe logs showing NBIO 7.0 ASIC initialization without PCI config, IOMMU, PSP, or RAS errors.
- Register readback checks where a caller writes a field via `REG_SET_FIELD` and confirms only the intended masked bits changed.
- IOMMU stress with DMA, GPU memory management, KFD/ROCm workloads, and page-request capable clients to catch `L2_*`, PDC, table-walker, and PPR regressions.
- Suspend/resume and GPU reset tests to confirm hardware defaults or driver restore paths leave parity status, indirect windows, IOMMU capabilities, and L2 controls coherent.
- RAS/error-injection or fault-observation tests, where available, to validate PSP parity status, counters, action controls, poison status, and APML error signaling.
- SR-IOV or multi-function PCI tests if bridge control, dummy config functions, steering, or per-device indirect config fields are touched by platform code.

### subset-b-003102: lines 83012-85506

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 83012-85506

## Scope

This chunk is a generated AMD NBIO 7.0 register shift/mask header segment. It contains only C preprocessor constants; there are no functions, structs, variables, allocation paths, locks, branches, loops, direct MMIO accesses, or persistence paths in this range.

The slice starts inside the `nbio_iohub_iommu_l2indx_l2indxcfg` address block, at the tail of L2B IOMMU controls. It then covers L2B shadow bus-number registers, L2B PSP hardware-error reporting, NB IOAPIC routing and shadow remap registers, two mirrored IOMMU L1 register sets for `PCIE0` and `IOAGR`, their L1 shadow and L1 PSP sub-blocks, the L2A IOMMU block and L2A shadow block, and finally the first `SMMU_IDR0` shift definitions through `PRI`. The remainder of `SMMU_IDR0` and its masks continue after this chunk.

Although this file is under a local `ceph-client` source mirror, this header is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this header range is to publish bit positions for NBIO 7.0 IOMMU, IOAPIC, PSP-error, and SMMU capability registers. Each generated hardware field is represented as:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when packing or extracting the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update the field.

The companion address file, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`, provides the matching `mm`, `ix`, or `smn` register locations. Runtime AMDGPU code combines those offsets with this shift/mask header through register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

## Important Macro Families

The opening L2B fragment completes part of `nbio_iohub_iommu_l2indx_l2indxcfg`. It includes L2B memory-power-gating thresholds and maintain counters, performance counter controls/counts for events 4 through 7, DVM request and invalidation page-size controls, SDP max-credit and parity-error-enable bits, and an ECO control dword. Earlier L2B cache, credit, error-rule, page-size, and power-gate enable fields are outside this chunk.

The `nbio_iohub_iommu_l2bshdw_l2bshdw` block defines shadowed subordinate bus-number fields for `PCIE0` ports 0 through 7 and `NBIF1` ports 0 through 1. These macros expose secondary and subordinate bus-number fields used when the hardware mirrors or consumes PCI bridge bus-range configuration.

The `nbio_iohub_iommu_l2bpsp_l2bpsp` block defines PSP-visible L2B hardware-error reporting. It includes enable/support bits, hardware-error valid/overflow status, lower and upper event-code capture registers, and a high-register `EV_CODE` nibble. This is diagnostic metadata for hardware errors; the header does not define status clear semantics.

The IOAPIC configuration block defines feature enables, bridge interrupt routing for bridge groups `BR0` through `BR8`, serial interrupt status, scratch registers, clock-gating controls, SDP port disconnect hysteresis, four IOAPIC performance counters with upper dwords, and page-slave hysteresis. The matching IOAPIC shadow block defines programmed device/function remap fields for `PBr0` through `PBr8`.

The `nbio_iohub_iommu_l1_PCIE0_iommul1cfg` and `nbio_iohub_iommu_l1_IOAGR_iommul1cfg` blocks are mirrored IOMMU L1 front-end definitions for the PCIe0 path and IOAGR path. Each block defines four L1 performance counters, sideband location, L1 control registers, bank select/disable fields, 32 work-queue entry-status fields plus invalidation status, debug sticky bits, program-memory power-gating controls, clock-gating controls, guest-address checking, feature support reporting, page-slave status, ATS response timers, traffic-stall controls for DMA and host request/response channels, SDP credit limits, and ECO control.

The L1 control families are the densest part of the chunk. `L1_CNTRL_0` covers unfilter/fragment behavior, read/write-only cache modes, L2 credits, L1 bank and entry sizing, error-event detect disable, host response pass behavior, and interrupt half-dword handling. `L1_CNTRL_1` covers cache bypass, cache and general parity enablement, DTE disable, work-queue entry disable mask, send-filter disable, ordering, global cache invalidation, timeout pulse selection, cache selection policy, pretranslation/untranslated filters, strict VC ordering, and chained DMA use. `L1_CNTRL_2` includes L1 disable, MSI-to-HT remap disable, ATS abort behavior, ATS/data error signaling, CPD response mode, SDP parity, and VC flush invalidation controls. `L1_CNTRL_4` covers multiple ATS responses, timeout pulse extension, ATS response memory-type sending, and internal graphics unit ID validity.

The L1 shadow blocks for `PCIE0` and `IOAGR` expose the IOMMU MMIO view seen through shadow registers. Both include device-table size fields for banks 0 through 7, MMIO control enables for IOMMU/event logging/interrupts/command buffer/PPR/GT/GA/TLPT, DTE segment enablement, exclusive base and limit windows, counter bank locks, and repeated performance counter match programming for two banks by four counters. Each counter instance has source, count-unit, and counter-active-control bits, plus optional PASID, domain, and device-id match/mask and enable fields.

The L1 PSP blocks for `PCIE0` and `IOAGR` define CPD error reporting and request capture: CPD support, valid/overflow status, request stream ID, request address low/high dwords, and an `AbortPreTrans` request-control bit. These fields are PSP/error-reporting integration points, not regular software state containers.

The `nbio_iohub_iommu_l2a_l2acfg` block defines the L2A side of the IOMMU cache/control plane. It includes performance counters 0 through 3, an L2 status dword, L2 controls for L1 cache acceptance, side PTE behavior, FIFO priorities, sequential invalidation burst limits, DTC/ITC/PTC-A cache controls, hash masks, way disable/access-disable controls, L2 credit controls, update-filter behavior, error-rule disable controls, clock gating, page-size controls, memory power gating thresholds/maintain counters, IP power-gate threshold/status/busy/firmware-exit fields, and an ECO dword.

The `nbio_iohub_iommu_l2ashdw_l2ashdw` block exposes L2A shadowed IOMMU MMIO control. It includes device-table sizes, IOMMU/GT/GA/SMIF/SMIF-log/GAM enables, DTE segment/privileged-abort/EPH controls, exclusive windows, four SMI filter registers with DID/valid/lock fields, capability mirrors, and writable capability/support fields such as IOTLB/EFR, PREF/PPR/NX/GT/GA/PC/HATS/US/GAM, PAS_MAX, DTE segment width, and EPH support.

The final `nbio_iohub_smmu_mmio_smmummiocfg` fragment only begins `SMMU_IDR0`. This assigned range includes shifts for S2P, S1P, TTF, COHACC, BTM, HTTU, DORMHINT, Hyp, ATS, PERFCTRS, ASID16, MSI, SEV, ATOS, and PRI. The corresponding masks and later `SMMU_IDR0` fields start after line 85506 and are outside this chunk.

## Control Flow

There is no executable control flow in this header. Runtime behavior occurs only in code that includes these generated constants:

1. AMDGPU or related platform code selects a register offset from `nbio_7_0_offset.h`.
2. It reads, composes, or updates a 32-bit register value through the AMD register access layer.
3. It applies this header's `__SHIFT` and `_MASK` macros directly or through `REG_SET_FIELD` and `REG_GET_FIELD`.
4. It writes a control value, decodes a capability/status value, polls hardware-owned status, clears sticky diagnostics, or exposes decoded state to higher-level IOMMU, PCIe, IOAPIC, PSP, SMMU, power-management, or debugging code.

Typical consumers are initialization and tuning paths for NBIO/IOMMU cache hierarchy, PCIe/IOAGR translation front-ends, interrupt routing, power/clock gating, ATS and DVM invalidation, hardware error reporting, performance counter programming, and suspend/resume restoration.

## State And Persistence Behavior

This file stores no software state and persists nothing to disk. It describes hardware-backed register state owned by the GPU, firmware/PSP, the NBIO/IOMMU blocks, IOAPIC routing hardware, and the host platform.

The represented state includes static capability bits, software-programmed control bits, hardware-updated status, sticky diagnostic/error captures, performance-counter selector/count state, bridge bus-number shadows, IOAPIC route/remap configuration, cache and translation-cache sizing/control, exclusive MMIO windows, PASID/domain/device-id performance-counter filters, SMI filter lock/valid state, power/clock-gating thresholds and status, and SMMU feature discovery. Some fields are read-only capabilities, some are writeable policy controls, some are volatile counters, and some may be write-one-to-clear or firmware-owned diagnostics. The generated masks do not encode access width, reset defaults, side effects, ordering requirements, or ownership rules.

Mirrored `PCIE0` and `IOAGR` L1 blocks should be treated as separate hardware instances with parallel layouts. The repeated shadow performance-counter match registers should be treated as bank/counter-indexed state rather than independent semantic features.

## Dependencies And Integration Points

The primary dependency is the generated NBIO 7.0 register database. This file must remain synchronized with:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`, which supplies the matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h`, which supplies reset/default values where generated.
- AMDGPU register helper macros and accessors, including `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

The meaningful integration surfaces are AMDGPU NBIO setup, GPU IOMMU/SMMU configuration, PCIe and IOAGR translation front-end policy, ATS/DVM invalidation handling, PPR/CPD and PSP error reporting, IOAPIC interrupt routing and bridge swizzling, performance monitoring, clock and memory power gating, page-size and exclusive-window programming, and debug or RAS-style hardware diagnostics.

These definitions also overlap generic platform domains: PCI bridge bus-number assignment, IOAPIC interrupt delivery, IOMMU translation and invalidation, PASID/domain/device matching, ATS/PRI capability discovery, MSI-capable SMMU behavior, power-management clock gating, and firmware-owned error capture. Consumers must pair each mask with the correct offset, instance, and access protocol.

## Risks And Edge Cases

- The chunk boundaries are artificial. It starts after the beginning of the L2B indexed block and ends before the `SMMU_IDR0` register definition is complete, so adjacent chunks are required for full L2B and SMMU analysis.
- These are untyped preprocessor constants. A stale shift or mask compiles cleanly while decoding or programming the wrong hardware bit.
- `PCIE0` and `IOAGR` L1 blocks are mechanically mirrored. Copy/paste mistakes can silently target the wrong instance or use the wrong prefix while producing plausible register values.
- L1 and L2 controls include translation, cache, ordering, parity, ATS, DVM, and flush behavior. Incorrect values can cause stale translations, DMA faults, ordering violations, missed invalidations, or hangs under load.
- Work-queue status and invalidation status fields are hardware-owned and may be transient. Generic read/modify/write treatment can mis-handle live status or poll the wrong completion condition.
- PSP CPD and L2B hardware-error status fields may be sticky, overflow-sensitive, firmware-owned, or write-one-to-clear. Careless updates can lose first-error evidence or mask later diagnostics.
- IOAPIC bridge routing and shadow remap fields are interrupt-delivery sensitive. Incorrect group, swizzle, internal map, or DevFn remap values can misroute INTx-style interrupts or break platform enumeration assumptions.
- Power and clock gating fields interact with idle detection and wakeup. Aggressive threshold, hysteresis, or gate-enable programming can create intermittent access failures or resume/runtime-PM regressions.
- Counter match registers combine source selection, PASID/domain/device-id filters, masks, enables, locks, and active-control bits. Partial updates can collect misleading performance data or leave counters locked to stale filters.
- Reserved fields are explicitly named in many masks. Consumers must preserve reserved bits according to hardware guidance; generated masks alone do not tell whether writing zero is safe.
- Capability mirrors such as IOMMU, SMMU, ATS, PRI, MSI, GT/GA, PPR, EFR, HATS, and GAM should not be treated as independent software policy without checking hardware/firmware ownership and platform support.

## Test Signals

Useful validation is primarily build-time and hardware-integration oriented:

- Build AMDGPU with NBIO 7.0 support enabled; missing, renamed, or duplicated macros should surface in NBIO/IOMMU/SOC15 include paths that consume this generated header.
- Compare this range against `nbio_7_0_offset.h` and `nbio_7_0_default.h` to confirm register names, address blocks, repeated `PCIE0`/`IOAGR` layouts, L1 shadow bank/counter strides, and L2A/L2B naming remain synchronized.
- Boot affected hardware and confirm IOMMU enablement, ATS/DVM invalidation, DMA workloads, and PCIe/IOAGR request paths operate without translation faults or hangs.
- Exercise suspend/resume and runtime power-management flows while monitoring L1/L2 page-slave status, clock-gating, memory-power-gating, and power-gate busy/status fields.
- Validate IOAPIC bridge interrupt routing by exercising INTx/MSI-adjacent paths and checking for lost, swizzled, or misrouted interrupts on bridge groups `BR0` through `BR8`.
- Use available hardware diagnostics or error-injection paths to verify L2B PSP hardware-error valid/overflow/event-code fields and L1 PSP CPD request capture fields behave as expected.
- Program and read L1/L2/IOAPIC performance counters where supported; counter selection, upper/lower count fields, PASID/domain/device-id filters, and lock bits should match expected traffic.
- Run IOMMU stress with PASID, ATS, PRI, and invalidation-heavy workloads; stale translations, CPD/PPR events, or unexpected work-queue/invalidation status values can indicate mask/offset drift.
- Confirm reserved bits are preserved in read/modify/write users and that control writes do not change hardware-owned status or sticky diagnostic fields unexpectedly.

## Chunk Notes

- Lines 83012-83104 are a tail fragment of `nbio_iohub_iommu_l2indx_l2indxcfg`, focused on L2B memory power gating, performance counters, DVM controls, SDP credits/parity, and ECO state.
- Lines 83105-83157 cover L2B shadowed bus-number fields for `PCIE0` ports 0-7 and `NBIF1` ports 0-1.
- Lines 83158-83189 cover L2B PSP hardware-error reporting.
- Lines 83190-83367 cover IOAPIC feature/routing/performance/power controls and IOAPIC shadow DevFn remap fields.
- Lines 83368-85091 cover mirrored `PCIE0` and `IOAGR` IOMMU L1, L1 shadow, and L1 PSP blocks.
- Lines 85092-85489 cover L2A IOMMU configuration and shadow MMIO/capability fields.
- Lines 85490-85506 only begin the SMMU MMIO `SMMU_IDR0` register; masks and remaining fields are outside this work item.

### subset-b-003103: lines 85507-88072

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 85507-88072

## Scope

This chunk covers lines 85507-88072 of the generated AMDGPU NBIO 7.0 shift/mask register header. The range contains C preprocessor constants only: `#define` names ending in `__SHIFT` or `_MASK`, plus generated address-block comments. It has no functions, structs, enums, executable statements, allocation, locking, or direct runtime side effects.

The slice starts in the middle of the `SMMU_IDR0` field definitions, continues through SMMU identification/control and stream-table masks, then covers four generated address blocks:

- `nbio_iohub_nb_ioagrcfg_ioagr_cfgdec`
- `nbio_sst0_sst_core_sstcorecfg`
- `nbio_sst1_sst_core_sstcorecfg`
- `nbio_iohub_iommu_l2mmio_l2mmiocfg`
- the beginning of `nbio_iohub_nb_nbcfg_nb_cfgdec`
- the beginning of `nbio_iohub_iommu_l2_iommul2cfg`

The range ends inside the first fields of `IOMMU_L2_2_IOMMU_COMMAND`, so the later merge lane should reconcile that split with the next chunk.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield companion to the NBIO 7.0 offset/default/SMN headers. This chunk gives AMDGPU code symbolic bit positions and masks for interpreting or constructing register values in NBIO/SMMU/IOMMU, IOAGR, SST, and NB configuration blocks.

Major hardware responsibilities represented here:

- SMMU identity and control discovery: `SMMU_IDR*`, `SMMU_IIDR`, `SMMU_AIDR`, `SMMU_CR0`, `SMMU_CR0ACK`, `SMMU_CR2`, `SMMU_GBPA`, and stream-table base/config fields.
- IOAGR clock gating, request/response decode overrides, user-bit bypass, SDP port behavior, performance counters, power-gating controls, SION scheduling/credit tables for clients 0-3, and live-lock watchdog threshold.
- SST core 0 and SST core 1 clock/enable/RSMU identity/statistics, SION scheduling tables, credit allocations, wrapper clock-gating controls, and backdoor registers.
- IOMMU L2 MMIO programming: device table, command/event/PPR/GA log bases, control and status fields, exclusion windows, extended feature reporting, SMI filters, MSI capability/address/data, MARC relocation windows, queue head/tail pointers, overflow/auto-response controls, and IOMMU performance counter banks.
- NB configuration space for `NB_NBCFG2_*`: PCI identity/header fields, command/status, subsystem IDs, PCI control, SMN indexed access windows, scratch registers, arbitration/PME fields, DRAM base/top registers, mutex registers, and NB performance control.
- The initial fields of `IOMMU_L2_2_*`, beginning with vendor/device ID and command bits.

## Important APIs, Types, And Macros

There are no callable APIs or C types. The public surface is generated macro metadata. Each register field normally has a pair:

- `REGISTER__FIELD__SHIFT`: zero-based bit position.
- `REGISTER__FIELD_MASK`: contiguous or single-bit mask for the encoded field.

Important macro groups in this range:

- `SMMU_IDR0` through `SMMU_IDR5`: capability discovery masks for SMMU stage support, translation table formats, coherency, broadcast TLB maintenance, HTTU, dormant hints, hypervisor support, ATS/PRI/MSI/SEV/ATOS support, ASID/VMID width, endianness, stall/termination models, stream table levels, RAS, output address size, supported granules, and stall maximum.
- `SMMU_CR0` and `SMMU_CR0ACK`: enable and acknowledgement bits for SMMU, PRI queue, event queue, command queue, ATS check, and VMW mode. These paired fields are important because software typically programs `CR0` and waits for `CR0ACK` to match enabled state.
- `SMMU_STRTAB_BASE_HI`, `SMMU_STRTAB_BASE_LO`, and `SMMU_STRTAB_BASE_CFG`: stream-table address, read-allocate hint, log2 size, split, and format fields.
- `IOAGR_GLUE_CG_LCLK_CTRL_{0,1}`: clock-gating hysteresis and per-clock soft overrides.
- `IOAGR_REQDECODE_OVERRIDE` and `IOAGR_RSPDECODE_OVERRIDE`: eight 4-bit client override slots for request and response decode routing.
- `IOAGR_PERF_CNTL` and `IOAGR_PERF_COUNT{0..3}{,_UPPER}`: four event selectors and 56-bit-style counters split into lower 32-bit and upper 24-bit fields.
- `IOAGR_PGMST_CNTL` and `IOAGR_PGSLV_CNTL`: power-gating hysteresis, enable, idleness counting, firmware power-gating exit, and slave idle hysteresis fields.
- `IOAGR_SION_*`: repeated 32-bit lower/upper SION scheduling and credit-allocation words for clients 0-3, covering S0/S1 request, read-response, write-response burst targets and time slots, plus request/data/read-response/write-response pool credit allocation.
- `SST_CORE{0,1}_*`: duplicated SST core field masks for clock control, enable control, RSMU host/client identity, statistics, SION burst/slot tables, wrapper clock-gating controls, credit allocation, and backdoor/debug words.
- `IOMMU_MMIO_*`: extensive IOMMU L2 MMIO fields. Notable subgroups include base-address high/low fields for device tables and queues, `IOMMU_MMIO_CNTRL_0` feature enables, `IOMMU_MMIO_STATUS_0` queue/overflow/interrupt state, MSI capability and MSI address/data fields, MARC base/relocation/length windows 0-3, queue head/tail pointers, PPR auto-response and overflow thresholds, and performance counter configuration/match/report fields.
- `NB_NBCFG2_*`: PCI config fields for a second NB config instance, including command enables, target/master abort status, class/header/subsystem values, PCI control bits (`PMEDis`, `SErrDis`, `MMIOEnable`, `HPDis`), SMN index/data windows 0-6, index-data mutex unlock bits, DRAM slot base/top fields, and global NB performance counter controls.

## Address-Block Layout

Generated comments in this chunk divide the range into hardware blocks:

- The opening lines continue an SMMU MMIO/register section from the previous chunk, beginning mid-`SMMU_IDR0` and then defining complete SMMU ID, architecture ID, control, global bypass/abort, and stream-table fields.
- `nbio_iohub_nb_ioagrcfg_ioagr_cfgdec` covers IO aggregator control. It begins with clock gating and decode override registers, then expands into performance/power controls and a large matrix of SION scheduling and credit allocation registers for clients 0-3.
- `nbio_sst0_sst_core_sstcorecfg` and `nbio_sst1_sst_core_sstcorecfg` are almost parallel SST core blocks. They expose clock/enable, RSMU HCID/SIID identity, statistics, SION scheduling, credit allocation, wrapper clock-gating, and backdoor registers.
- `nbio_iohub_iommu_l2mmio_l2mmiocfg` is the largest block in the chunk. It defines masks and shifts for IOMMU L2 MMIO setup, queues, interrupts, feature reporting, MARC windows, status, and performance counters.
- `nbio_iohub_nb_nbcfg_nb_cfgdec` starts the `NB_NBCFG2_*` PCI/NB config block and is complete through `NB_NBCFG2_NB_SMN_DATA_6`.
- `nbio_iohub_iommu_l2_iommul2cfg` starts at the end with `IOMMU_L2_2_IOMMU_VENDOR_ID`, `IOMMU_L2_2_IOMMU_DEVICE_ID`, and part of `IOMMU_L2_2_IOMMU_COMMAND`.

## Control Flow

This header has no direct control flow. Runtime control flow is in AMDGPU and platform driver code that includes the generated register metadata and uses it with register access helpers.

Typical consumer flow is:

1. Code includes `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and sometimes `nbio_7_0_default.h`/`nbio_7_0_smn.h`.
2. Driver code computes a register address from the offset/SMN header.
3. It reads or writes the value through AMDGPU helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, or related NBIO indexed-access paths.
4. It extracts or updates fields using these `__SHIFT` and `_MASK` constants, usually through `REG_GET_FIELD`, `REG_SET_FIELD`, or equivalent mask/shift expressions.

The flow is especially sequencing-sensitive for IOMMU/SMMU setup. For example, code that enables queues in `SMMU_CR0` or `IOMMU_MMIO_CNTRL_0` must respect acknowledgement/status fields such as `SMMU_CR0ACK`, queue head/tail pointers, overflow bits, and interrupt enables. This header only supplies the bit encodings; it does not enforce ordering, polling, reserved-bit preservation, or write-one-to-clear behavior.

## State And Persistence Behavior

The macros are compile-time constants and hold no mutable state. The state they describe lives in hardware registers, MMIO windows, PCI configuration registers, and queue-memory pointers.

State represented by this chunk includes:

- SMMU capability and enable state, including ID registers, stream-table base/configuration, control acknowledgements, and global bypass/abort fields.
- IOAGR runtime control state: clock-gating overrides, decode overrides, SDP early clock request behavior, performance counter selections/counts, power-gating hysteresis, SION scheduling tables, pool credits, and live-lock threshold.
- SST core state for both core instances: clock and enable controls, RSMU identity fields, statistics counters, SION scheduling and credits, and backdoor/debug words.
- IOMMU L2 state: device-table and queue base addresses, command/event/PPR/GA log queue head/tail pointers, IOMMU feature enables, exclusion windows, SMI filter registers, MSI routing, MARC relocation windows, overflow/active/status bits, and performance counter filters/matches/reports.
- NB config state: PCI command/status, subsystem and class/header fields, MMIO enablement, hot-plug/PME controls, indexed SMN access registers, scratch registers, mutex unlock bits, DRAM base/top fields, and global counter reset/shadow controls.

Persistence is external to this header. Across GPU reset, BACO, runtime suspend/resume, hot reset, or firmware handoff, these registers may reset, retain values, or require explicit restore depending on power domain and ASIC behavior. Driver code must preserve reserved bits and reinitialize hardware-visible state using the companion offset/default metadata and runtime policy.

## Dependencies And Integration Points

Direct dependencies are limited to the C preprocessor and include ordering. Semantic dependencies include:

- `nbio_7_0_offset.h` for register offsets corresponding to these bitfields.
- `nbio_7_0_default.h` for reset/default values that use the same register names.
- `nbio_7_0_smn.h` for SMN-accessible address definitions.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, SOC15 setup code, and SMU include bundles that pull in NBIO 7.0 generated headers.
- AMDGPU register helper macros and field helpers used to apply these shifts/masks.
- Linux/AMDGPU integration paths for PCIe/NBIO discovery, doorbells, reset, BACO, power management, IOMMU/SMMU queue programming, MSI/AER-like interrupt routing, and performance counter diagnostics.

Cross-reference searching in the AMDGPU tree shows many direct matches are generated headers rather than handwritten code. That is expected for AMD register catalogs: handwritten consumers often refer to a smaller subset through generic helper patterns, while the generated headers preserve the complete silicon register description for build-time availability and diagnostics.

## Risks And Edge Cases

- Generated register metadata drift is the primary risk. A wrong shift or mask can silently corrupt neighboring fields during `REG_SET_FIELD` operations or decode the wrong status bit during polling.
- The chunk begins and ends mid-register-family. `SMMU_IDR0` starts in the previous chunk, and `IOMMU_L2_2_IOMMU_COMMAND` continues in the next chunk. The final per-file document must avoid treating those partial boundaries as complete register definitions.
- Reserved-bit handling is critical. Many IOMMU and PCI/NB fields include explicit `Reserved*` masks. Consumers should preserve reserved bits on read-modify-write unless the hardware specification says otherwise.
- IOMMU/SMMU queue and base-address fields are high impact. Incorrect masks for device-table bases, command/event/PPR/GA queues, or head/tail pointers can break DMA translation, lose events, or hang command processing.
- Control/status ordering is not encoded here. `SMMU_CR0`/`SMMU_CR0ACK`, IOMMU enable bits, queue run bits, overflow bits, and MSI enables need correct runtime sequencing outside this header.
- IOAGR and SST repeated SION table fields are easy to mis-index. Client, stream (`S0`/`S1`), request/read-response/write-response, burst-target/time-slot, and lower/upper naming must match the intended hardware register.
- Clock and power controls are platform-sensitive. Incorrect use of `SOFT_OVERRIDE_CLK*`, power-gating hysteresis, early clock request, or SST clock enable fields can cause idle-power regressions or access timeouts.
- PCI/NB SMN indexed access and mutex fields are shared-access hazards. Code using `NB_SMN_INDEX_*`, `NB_SMN_DATA_*`, or `NB_INDEX_DATA_MUTEX*` must coordinate access and respect unlock semantics.
- Performance counters and match registers may affect observability rather than functional state, but bad masks can make diagnostics misleading or break counter bank ownership/locking.

## Test Signals

Useful validation signals for changes touching this chunk:

- Compile AMDGPU/SOC15 code with NBIO 7.0 headers included; malformed generated lines, renamed macros, or collisions should fail at build time.
- Regenerate `nbio_7_0_sh_mask.h` from the authoritative AMD register database and compare the generated diff, especially around split boundaries and repeated IOAGR/SST/IOMMU counter blocks.
- Static-check mask/shift consistency: each mask should align with its shift and field width; repeated client/core/counter blocks should differ only by intended index/name.
- Boot/probe NBIO 7.0 hardware and watch AMDGPU, PCIe, and IOMMU logs for translation, queue, MSI, AER, or NBIO access errors.
- Exercise GPU reset, suspend/resume, BACO entry/exit, and PCIe hot/reset flows while checking that SMMU/IOMMU control/status bits reach expected states.
- Run workloads that stress DMA translation and queue activity, including graphics, SDMA, video, and KFD/compute where applicable; monitor IOMMU event/PPR/GA logs and overflow status fields.
- Validate doorbell, HDP, and SMN-indexed paths indirectly through normal queue submission and through debug tooling that reads NBIO/IOMMU counters.
- For power-management validation, compare idle/resume behavior with IOAGR/SST clock-gating and power-gating controls, watching for access timeouts and unexpected clock residency.

## Cross-Chunk Notes

This is a chunk-level report only. Later reconciliation should merge it with adjacent `nbio_7_0_sh_mask.h` chunk reports, preserving the full source path. The merge should stitch the partial `SMMU_IDR0` definition from the previous range and the partial `IOMMU_L2_2_IOMMU_COMMAND` definition from the next range, and should deduplicate repeated descriptions of IOMMU L2 MMIO families where adjacent chunks cover earlier/later instances.

### subset-b-003104: lines 88073-90484

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 88073-90484

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It covers 2,412 source lines and 2,172 `#define` field-layout macros. There are no functions, structs, enums, local variables, locks, allocations, or executable statements in this range.

The range starts in the middle of `IOMMU_L2_2_IOMMU_COMMAND`, after the first command shifts and before the command masks. It then covers the rest of the `nbio_iohub_iommu_l2_iommul2cfg` block, all of the small `nbio_iohub_nb_pciedummy0_pciedummy_cfgdec` block, all of the `nbio_pcie0_bifplr0_cfgdecp` bridge/port block, and the start of `nbio_pcie0_bifplr1_cfgdecp` through `BIFPLR1_2_SECONDARY_STATUS`. The merge lane should reconcile the boundary registers with adjacent chunks before treating the IOMMU command or BIFPLR1 block as complete.

Although the path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata. It has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield-geometry half of AMD's generated NBIO 7.0 register interface. For each register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to place or extract a field.
- `<REGISTER>__<FIELD>_MASK`, the encoded bit mask used to isolate, preserve, clear, or update that field.

This chunk describes field layouts for an NBIO IO hub IOMMU L2 PCI/SMMU configuration aperture, a dummy PCI configuration function, and a large PCIe bridge/root-port style `BIFPLR0_2` configuration surface. The fields are intended to be combined with generated register address/default metadata and AMDGPU register helpers; the macros alone do not perform reads, writes, polling, error handling, or persistence.

## Important Macro Families

The `IOMMU_L2_2` section exposes the IOMMU L2 configuration-space and SMMU identity surface:

- PCI-like identity and command/status fields: vendor/device ID, command enables for IO, memory, bus mastering, parity, SERR, and interrupt disable, plus status bits for interrupt status, capability-list presence, master data error, target/master aborts, system error, and parity error.
- Class/header fields: revision ID, programming interface, subclass, base class, cache line size, latency, header type, BIST, subsystem/vendor adapter ID, capability pointer, interrupt line, and interrupt pin.
- IOMMU capability fields: capability header, base-address low/high, range/unit/bus/device fields, MSI vector numbers, GVA/PA/VA sizing, architecture mode, DVM mode, and SMMU MMIO enable/lock.
- MSI and MSI mapping fields: MSI capability header, enable and multiple-message fields, 64-bit address support, MSI address/data words, and MSI mapping capability/address controls.
- Write-side or firmware-visible IOMMU controls: adapter ID write register, control register fields for command buffer enable, event log enable, MMIO enable, interrupt enable, completion wait behavior, guest translation/cache controls, PPR enable, GA log enable, SMI filter controls, MSI controls, GA tag and invalidation tag controls, and address/data controls for MMIO windows.
- Range and dummy/control registers: range valid/unit/bus/device fields, `DSFX_CONTROL`, dummy data registers, poison/DVM controls, IOHC/L2 DMA request and host response stall controls.
- SMMU MMIO identification registers: `IDR0`, `IDR1`, `IDR2`, `IDR3`, `IDR5`, `IIDR`, and `AIDR` fields describing SMMU architecture capabilities such as stage support, context banks, stream matching, translation levels, page granules, ASID/VMID bits, coherency, endianness, secure-state support, PTW behavior, and architecture revision.

The `NB_PCIEDUMMY0_2` section is a compact dummy PCI configuration block. It defines combined device/vendor ID, status/command, class-code/revision, header type, and a write-oriented header-type byte. These fields model a minimal PCI config surface rather than an active algorithm.

The `BIFPLR0_2` section is a full PCIe bridge/root-port style configuration layout:

- Standard PCI bridge header fields: vendor/device ID, command/status, revision/programming interface/subclass/base class, cache line, latency, header/BIST, primary/secondary/subordinate bus numbers, IO base/limit, secondary status, memory and prefetchable memory windows, upper prefetchable base/limit, high IO base/limit, capability pointer, interrupt line/pin, IRQ bridge control, and extended bridge control.
- Power-management capability fields: PM capability list linkage, version, PME and D-state support, PME enable/status, data select/scale, power state, B2/B3 support, bus power/clock control, and PM data.
- PCI Express capability fields: PCIe capability list/header, device capabilities/control/status, link capabilities/control/status, slot/root capability/control/status, and PCIe 2.0 device/link/slot capability/control/status registers.
- MSI and subsystem ID fields: MSI capability header/control, MSI message address/data, 64-bit data, subsystem ID capability fields, and MSI mapping capability/address fields.
- Vendor-specific and virtual-channel fields: PCIe vendor-specific enhanced capability headers and payload words, VC port capabilities/control/status, and VC0/VC1 resource capability/control/status fields.
- Device serial number and AER fields: device serial number dwords; AER enhanced capability, uncorrectable/correctable status, masks and severities, AER capability/control, header logs, root error command/status, source ID, and TLP prefix logs.
- Secondary PCIe/link training fields: secondary enhanced capability, link control 3, lane error status, and lane 0 through lane 15 equalization controls.
- ACS, multicast, L1 PM substate, DPC, RP PIO, and ESM fields: ACS capability/control, multicast address/receive/block/overlay registers, L1 PM substate capability/control, Downstream Port Containment control/status/source, RP PIO status/mask/severity/sys-error/exception/header/prefix logs, and ESM capability/status/control/capability bitmaps.

The `BIFPLR1_2` section begins the next PCIe bridge/root-port style block. This chunk includes only its standard identity/header region through secondary status: vendor/device ID, command/status, revision/class bytes, cache/latency/header/BIST, bus-number/latency, IO base/limit, and secondary-status fields. Memory windows and later capabilities continue in the next chunk.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public surface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only bit positions and masks for 8-, 16-, and 32-bit PCI/NBIO/SMMU register words.

The macros do not encode register addresses, access permissions, write-one-to-clear behavior, reset domains, polling requirements, ordering barriers, firmware ownership, or side effects. Consumers must combine these field definitions with sibling generated metadata:

- `nbio_7_0_default.h` provides reset/default values for the `IOMMU_L2_2`, `NB_PCIEDUMMY0_2`, `BIFPLR0_2`, and `BIFPLR1_2` register families.
- `nbio_7_0_offset.h` and `nbio_7_0_smn.h` provide the address/SMN side for the broader NBIO 7.0 register database, although these exact `*_2` names are more visible in default and shift/mask metadata than in local C call sites.
- AMDGPU code applies the macros through helper patterns such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET` where the target register has a matching address symbol.

## Control Flow

This header has no local runtime control flow. Runtime flow is external and typically looks like:

1. AMDGPU/NBIO/platform code selects a hardware register from generated offset or SMN metadata.
2. The code reads a 32-bit register value from the correct aperture.
3. It extracts a field with the `__SHIFT` and `_MASK` constants, or composes a new value by clearing the mask and inserting a shifted field value.
4. The decoded or written value affects IOMMU configuration, PCIe bridge enumeration, interrupt routing, error reporting, link training, power management, SMMU capability reporting, DPC/RP PIO diagnostics, or capability exposure.

The names imply several hardware-managed flows outside this header: IOMMU command/event/PPR/GA-log enablement, MSI delivery and MSI remapping, SMMU identification reporting, PCI bridge resource-window programming, PME and D-state transitions, PCIe link retraining and equalization, VC resource negotiation, AER/DPC/RP PIO error capture, ACS isolation controls, multicast overlay/blocking controls, and L1 PM substate negotiation.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO IOMMU, SMMU, dummy PCI, and PCIe bridge/root-port configuration registers. Persistence depends on GPU reset domain, PCIe reset, function-level reset, firmware/BIOS programming, host PCI core configuration, suspend/resume restore, and explicit driver writes.

Represented state includes PCI identity/class/header fields, command/status bits, bridge bus numbers and resource windows, interrupt line/pin and MSI routing state, IOMMU base/range/control fields, SMMU capability ID registers, power-management and PME state, PCIe link/device/slot/root controls and statuses, VC/ACS/multicast controls, AER/DPC/RP PIO status/mask/log registers, lane equalization state, and ESM capability bitmaps.

Several fields are likely status or latched hardware state, such as PCI error status, link training/equalization status, AER/DPC/RP PIO logs, lane errors, and MSI pending data. Others are configuration controls that software or firmware may write, including command enables, bridge windows, power-management controls, MSI enables, IOMMU logging/translation controls, ACS controls, multicast controls, DPC enables, and ESM controls. The mask header does not distinguish read-only, read/write, write-one-to-clear, or reserved semantics; callers must preserve reserved bits and follow hardware documentation.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database. It must remain synchronized with sibling generated headers:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h`
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h`

Direct include users in this tree are `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. `nbio_v7_0.c` shows the intended integration style: include default/offset/shift-mask/SMN headers together and use AMDGPU register helpers around generated symbols. The exact `IOMMU_L2_2`, `NB_PCIEDUMMY0_2`, and `BIFPLR*_2` symbols in this chunk are not directly exercised by local `.c` files in the visible tree, so they are best treated as generated hardware metadata for platform, firmware, diagnostic, or future NBIO access paths rather than active high-level driver logic here.

The PCIe portions also depend on PCI/PCIe architectural semantics for standard config space, bridge windows, PM capabilities, MSI, PCIe capabilities, AER, VC, ACS, multicast, L1 PM substates, DPC, and RP PIO. The SMMU portions depend on ARM SMMU-style ID register semantics as exposed through AMD NBIO's IOMMU L2 MMIO surface.

## Risks And Edge Cases

- Generated shift/mask drift can compile successfully while causing software to decode or write the wrong hardware bit. For this chunk that can affect IOMMU enablement, interrupt delivery, PCI bridge windows, PCIe link state, AER/DPC error handling, or SMMU capability reporting.
- The chunk starts and ends mid-block. Adjacent chunks are required for complete `IOMMU_L2_2_IOMMU_COMMAND` and `BIFPLR1_2` coverage.
- Many registers contain reserved fields represented as explicit macros. Writers must preserve reserved bits unless the hardware specification requires a defined value.
- Status and error fields may be write-one-to-clear or latch-on-error at the hardware level. The masks make those bits easy to target but do not communicate clearing rules.
- IOMMU command/event/PPR/GA-log controls, MMIO enable/lock fields, MSI mapping, and SMMU identification fields can interact with firmware, IOMMU groups, interrupt remapping, and host memory isolation. Incorrect writes can break DMA translation or interrupt delivery.
- PCI bridge bus/resource-window fields are system-visible. Bad masks or writes can misroute IO/MMIO windows, hide downstream devices, or corrupt host PCI resource accounting.
- PCIe link, slot, root, VC, ACS, multicast, L1 PM, DPC, RP PIO, and ESM controls affect topology behavior, isolation, power, recovery, and error reporting. Code that writes them needs topology checks and hardware-specific sequencing.
- The `BIFPLR0_2` block is large and mechanically repetitive; generation errors can be localized to one capability family and missed if tests only cover enumeration or only inspect standard PCI header fields.
- Exact symbol availability differs across NBIO generations. For example, some `BIFPLR*_2` offset symbols are visible in neighboring NBIO 7.7.0 headers, while this NBIO 7.0 chunk mainly exposes shift/mask and default metadata for these names.

## Test Signals

- Build AMDGPU with NBIO 7.0 and SMU10 include paths enabled. Compile-time coverage catches missing generated symbols used by `nbio_v7_0.c`, `soc15.c`, and power-management include stacks.
- Run generated-header consistency checks: every field with a `__SHIFT` should have a compatible `_MASK`, masks should align with their shift, and fields within a register should not overlap except where the hardware register intentionally aliases bytes or words.
- Cross-check this chunk against `nbio_7_0_default.h` so every `IOMMU_L2_2`, `NB_PCIEDUMMY0_2`, `BIFPLR0_2`, and visible `BIFPLR1_2` register has a corresponding generated default where expected.
- Cross-check address coverage against `nbio_7_0_offset.h` and `nbio_7_0_smn.h`; missing address symbols should be treated as metadata coverage gaps or as registers accessed through a different aperture/generation-specific path.
- On supported NBIO 7.0 hardware, validate PCI enumeration, bridge bus/resource windows, MSI delivery, power-management state transitions, AER/DPC reporting, link retraining/equalization status, ACS behavior, L1 PM substate behavior, and reset/suspend/resume restore.
- For IOMMU/SMMU paths, validate command/event/PPR/GA-log enablement, MSI vector programming, MMIO base/range decoding, SMMU ID register values, DMA translation behavior, and interrupt remapping behavior against firmware and host IOMMU expectations.
- For error-path testing, inject or observe AER/DPC/RP PIO conditions and confirm that status, mask, severity, source-ID, header-log, and prefix-log fields decode correctly and that clearing code does not disturb unrelated or reserved bits.

### subset-b-003105: lines 90485-92893

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 90485-92893

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,176 `#define` field-layout macros for PCI/PCIe bridge and PCIe extended capability registers in the `BIFPLR1_2` logical root-port block and the beginning of the next `BIFPLR2_2` block. There are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts in the tail of `BIFPLR1_2_SECONDARY_STATUS`, beginning with `PARITY_ERROR_DETECTED__SHIFT` and the status masks. It then covers the rest of the `BIFPLR1_2` PCI bridge configuration, PCI Power Management, PCIe capability, MSI, subsystem ID, MSI mapping, vendor-specific, virtual-channel, device-serial-number, advanced error reporting, secondary PCIe, ACS, multicast, L1 PM substate, DPC, RP PIO, and ESM field definitions. After the `addressBlock: nbio_pcie0_bifplr2_cfgdecp` marker, it begins the mechanically similar `BIFPLR2_2` block from vendor/device/class registers through `BIFPLR2_2_PCIE_VC0_RESOURCE_STATUS`, ending after only the first `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP__PORT_ARB_CAP__SHIFT` field. Adjacent chunks are required for the complete `BIFPLR1_2_SECONDARY_STATUS` and `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP` register layouts.

Although this source tree is under a `ceph-client` mirror path, this file is AMDGPU hardware register metadata and has no direct distributed-filesystem behavior.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield geometry half of AMD's generated NBIO 7.0 register interface. For each register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to extract or place a field.
- `<REGISTER>__<FIELD>_MASK`, the encoded bit mask used to isolate, preserve, clear, or update that field.

This chunk maps the configuration-space view of NBIO PCIe logical root ports. The macros let AMDGPU code decode PCI bridge windows, capabilities, link state, error latches, virtual-channel arbitration, message-signaled interrupts, ACS/multicast controls, L1 PM substates, downstream port containment, root-port PIO error logs, and ESM metadata without embedding raw bit positions at call sites.

## Important Macro Families

The `BIFPLR1_2` PCI bridge and conventional capability fields cover:

- Bridge resource routing: memory base/limit, prefetchable memory base/limit including upper 32-bit registers, high I/O base/limit, capability pointer, interrupt line/pin, bridge control, and the extended bridge `IO_PORT_80_EN` bit.
- Secondary bus status and bridge control error state: capability-list presence, 66 MHz/fast back-to-back capability, master-data parity, DEVSEL timing, target/master aborts, system error, parity detected, parity response, SERR enable, ISA/VGA forwarding, master-abort mode, secondary-bus reset, and fast back-to-back enable.
- Power management capability: PM capability list linkage, PM version/features, D1/D2 and PME support, power state, no-soft-reset, PME enable/status, data select/scale, B2/B3 support, bus-power enable, and PM data.

The `BIFPLR1_2` PCIe capability fields cover:

- PCIe capability header and device identity: capability version, device type, slot implemented, interrupt message number, max payload support/size, extended tags, phantom functions, relaxed ordering, no-snoop, max read request size, FLR capability, bridge configuration retry, and device error enables/status.
- Link and slot state: supported/current link speed and width, ASPM/link PM support, L0s/L1 exit latencies, clock power management, surprise-down reporting, data-link-layer active reporting, bandwidth notification, ASPM/RCB/common-clock/extended-sync/clock-power bits, retraining, slot-clock config, link training, data-link-layer active, slot power/controller fields, attention/power indicators, hot-plug events, MRL sensor, command-completed, presence detect, and electromechanical interlock state.
- Root-port control/status: PME interrupt enables, CRS software visibility, PME requester ID/status/pending, and root error command/status/source identifiers for advanced error reporting.
- PCIe Capability 2 registers: completion timeout ranges and disables, ARI forwarding, atomic operation routing/completion/request enables, 32/64/128-bit CAS support, no-RO PR-PR passing, LTR/OBFF support, end-to-end TLP prefix support and blocking, target link speed, compliance controls, de-emphasis, equalization status, and lane error/equalization controls.

The `BIFPLR1_2` extended capability and diagnostics section includes:

- MSI and MSI mapping: capability linkage, enable/multiple-message fields, 64-bit/per-vector support, message address/data registers, MSI map enable/fixed/type, and map base address.
- Subsystem/vendor-specific capabilities: SSID, vendor-specific enhanced capability list/header, two scratch vendor-specific registers, and device serial number DW1/DW2.
- Virtual channels: VC enhanced capability, port VC capabilities, VC arbitration table controls/status, VC0/VC1 resource capabilities, traffic-class to VC maps, VC IDs, VC enable bits, and negotiation-pending/status fields.
- Advanced Error Reporting: uncorrectable error status/mask/severity fields for data link protocol, surprise down, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, uncorrectable internal error, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable status/mask fields include receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, header-log overflow, and the matching AER capability/control and header/TLP-prefix logs.
- Secondary PCIe extended capability: link control 3, lane error status, and lane 0 through lane 15 equalization controls for downstream/upstream port transmitter preset fields and preset hints.
- ACS and multicast: ACS capability/control bits for source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, egress control vector size, and multicast overlay/receiver/blocking address fields.
- L1 PM substates: capability list, ASPM/PCI-PM L1.1/L1.2 support, common-mode restore time, T-power-on scale/value, L1.2 enable bits, PME-turnoff acknowledgement, timing values, and T-power-on programming.
- DPC and RP PIO error handling: DPC capability/list/control/status/source ID fields, trigger reason/extension/status/interrupt bits, RP PIO status/mask/severity/system-error/exception bitmaps, header and prefix logs, and implementation-specific log storage.
- ESM registers: ESM capability list, headers, status, control, and capability blocks `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`, including capability count, next pointers, supported event masks, interrupt/message controls, and capability-specific bitmaps.

The `BIFPLR2_2` section restarts the same register model for another NBIO PCIe root-port address block. In this chunk it covers conventional PCI identity/class/cache/latency/header/BIST/bus-number/resource/status registers, PM and PCIe capabilities, MSI, SSID, MSI mapping, vendor-specific registers, and virtual-channel definitions through VC0 status. It stops before the complete VC1 resource-capability masks appear.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated macro namespace. The constants are untyped preprocessor integer literals, mostly with an `L` suffix, and encode only field geometry.

These macros do not define register addresses, reset values, access permissions, write-one-to-clear behavior, polling timeouts, ownership rules, or side effects. Consumers must combine them with sibling NBIO metadata such as `nbio_7_0_default.h` for defaults and generated address headers for the actual register offsets, then use AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the PCIe/NBIO access path appropriate for the register.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects a `BIFPLR1_2_*` or `BIFPLR2_2_*` register address from generated NBIO address metadata.
2. It reads a hardware register, extracts fields with the `__SHIFT` and `_MASK` constants, or composes a write while preserving unrelated and reserved bits.
3. The decoded or written values participate in PCIe bridge setup, link capability reporting, error detection, interrupt delivery, power management, virtualization/isolation controls, and diagnostic logging.

The field names imply several asynchronous hardware flows that software must handle outside this header: link training/retraining, equalization, hot-plug and slot events, PME generation, MSI delivery, AER/DPC error capture, RP PIO exception logging, L1 substate entry/exit, virtual-channel negotiation, and ESM event reporting.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes state held in NBIO PCIe configuration and extended-capability registers. Persistence depends on the GPU reset domain, PCIe hot/warm reset, FLR, DPC containment/recovery, runtime power management, suspend/resume restore, firmware/BIOS programming, and explicit AMDGPU writes.

Represented state includes writable control bits, bridge window registers, capability list pointers, negotiated link state, error enables/masks/severity maps, sticky status latches, MSI address/data state, virtual-channel mappings, ACS and multicast policy, L1 PM substate timing values, DPC trigger/status/source identifiers, RP PIO logs, and ESM capability/status/control words. Some fields are read-only capability or live-status bits, some are writable controls, and some status/error fields may be sticky or write-one-to-clear; that behavior is not derivable from the shift/mask definitions alone.

## Dependencies And Integration Points

This chunk must remain synchronized with the rest of the generated NBIO 7.0 register set:

- `nbio_7_0_default.h` contains matching `smnBIFPLR1_2_*_DEFAULT` and `smnBIFPLR2_2_*_DEFAULT` values for many of these registers.
- Generated NBIO offset/SMN headers provide the actual register addresses used by AMDGPU register access helpers.
- AMDGPU PCIe/NBIO, error handling, virtualization/isolation, reset, power-management, and diagnostic code consumes these definitions indirectly through generated ASIC register include stacks.

The `BIFPLR*` names indicate bridge-interface logical root-port configuration windows. Integration points include kernel PCI enumeration and bridge resource assignment, AMDGPU device initialization, PCIe capability reporting, hot-plug/root-port event handling, AER and DPC recovery paths, MSI setup, ACS/IOMMU isolation policy, virtual-channel QoS setup, and low-power link-state management.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing software to decode or update the wrong PCIe configuration bit. Failures can surface as incorrect resource windows, broken MSI delivery, misreported PCIe capabilities, unstable link training, missed errors, or unsafe ACS/multicast policy.
- The chunk starts and ends mid-register-family. Whole-file research must reconcile the previous `BIFPLR1_2_SECONDARY_STATUS` shift fields and the following `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP` masks before treating those registers as complete.
- Many status and error registers are likely sticky or write-one-to-clear in hardware. A helper that writes a full register value using only these masks can accidentally clear diagnostic evidence or acknowledge events.
- Error mask/severity/sys-error fields are security and reliability sensitive: a wrong bit can suppress fatal reporting, over-report benign conditions, or route errors to the wrong recovery path.
- ACS, multicast, ARI, atomic operation, and virtual-channel controls affect isolation and ordering semantics. Incorrect programming can break peer-to-peer routing, IOMMU assumptions, traffic-class mapping, or device interoperability.
- Link control, equalization, ASPM, L1 substate, DPC, and hot-plug fields interact with asynchronous PCIe state machines. Call sites need timeouts and recovery paths for link training, equalization failure, DPC trigger races, and suspend/resume transitions.
- Reserved fields appear throughout the generated layouts. Writers must preserve reserved bits unless hardware documentation explicitly permits a value.
- `BIFPLR1_2` and `BIFPLR2_2` are mechanically similar. Copy/generation errors may affect one root-port instance only, making failures topology-dependent.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing or renamed generated symbols used by consumers.
- Run generated-header consistency checks: every non-reserved field should have a compatible `__SHIFT`/`_MASK` pair, masks should align with shifts, and repeated `BIFPLR1_2`/`BIFPLR2_2` layouts should match where the hardware block is intended to be identical.
- Cross-check these register names against sibling default and address headers so every field layout maps to a known register and reset/default value.
- On supported hardware, validate PCIe enumeration, bridge resource assignment, MSI programming, link speed/width negotiation, ASPM/L1 substate behavior, suspend/resume, FLR, GPU reset, and DPC recovery.
- Exercise error paths where possible: AER correctable/uncorrectable logging, root error command/status, RP PIO status/header/prefix logs, DPC trigger/source reporting, and ESM event/status reporting.
- For any code writing these registers, review register traces to confirm reserved bits are preserved, write-one-to-clear status fields are acknowledged deliberately, and temporary diagnostics restore MSI, ACS, VC, ASPM, DPC, and error-mask state afterward.

### subset-b-003106: lines 92894-95298

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 92894-95298

## Purpose

This chunk is an auto-generated AMD NBIO 7.0 register shift/mask slice for PCIe configuration-space fields. It covers the end of the `BIFPLR2_2` root-port configuration decode block, starting inside `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP`, then continues through many `BIFPLR2_2` PCIe extended capabilities. It then starts a new generated address block, `nbio_pcie0_bifplr3_cfgdecp`, and defines the standard and extended PCI/PCIe configuration fields for `BIFPLR3_2` through the `PCIE_DPC_ENH_CAP_LIST` header.

The file does not implement algorithms or direct register I/O. Its public surface is preprocessor constants that let AMDGPU code extract and compose fields from hardware registers using companion register offset/default headers.

## Public Surface In This Chunk

The exported API is a dense set of `#define` macros following the generated pattern:

- `REGISTER__FIELD__SHIFT` for the bit position of a field.
- `REGISTER__FIELD_MASK` for the field mask in the raw register value.

The first lines continue `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP` with virtual-channel resource fields such as `REJECT_SNOOP_TRANS`, `MAX_TIME_SLOTS`, and `PORT_ARB_TABLE_OFFSET`. The chunk then includes `BIFPLR2_2_PCIE_VC1_RESOURCE_CNTL` and `STATUS`, serial-number enhanced capability fields, AER status/mask/severity/control/log fields, secondary PCIe capability fields, per-lane equalization fields for lanes 0-15, ACS, multicast, L1 PM substate, DPC, RP PIO, and ESM register groups.

The new `BIFPLR3_2` block starts at the `// addressBlock: nbio_pcie0_bifplr3_cfgdecp` marker and exposes a root-port style PCI config space. It includes vendor/device IDs, command/status, revision/class-code bytes, bus-number and bridge-window registers, interrupt/bridge controls, PM capability, PCIe capability, MSI/MSI-map and SSID fields, vendor-specific enhanced capability fields, virtual channel resources, serial number, AER, secondary PCIe link/equalization, ACS, multicast, L1 PM substate, and the DPC enhanced capability header.

## Important Register Families

The `BIFPLR2_2` portion is mostly PCIe extended capability coverage. Virtual Channel fields expose traffic-class to VC mapping, port arbitration table load/select state, VC ID, VC enable, and negotiation status. Device Serial Number fields split the serial number into low/high doublewords. Advanced Error Reporting fields cover uncorrectable error status, masks, and severity for DLP, surprise-down, poisoned TLP, flow-control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, and poisoned TLP egress blocked. Correctable AER fields cover receiver, bad TLP/DLLP, replay rollover, replay timer timeout, advisory non-fatal, correctable internal, and header-log overflow conditions.

The `BIFPLR2_2` logging and root-error groups provide full-width header log and TLP prefix log masks, root error command/status bits, and error source IDs. The secondary PCIe group defines link control 3, lane error status, and uniform lane equalization controls for lanes 0 through 15 with downstream/upstream TX preset and RX preset-hint fields. ACS fields expose source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, and direct-translated P2P capability/control bits.

The `BIFPLR2_2` multicast and power-management groups include multicast group count, enable, base address, receive/block masks, overlay BAR settings, and L1 PM substate support/control fields. The DPC and RP PIO groups expose containment capability/control/status, error source IDs, PIO status/mask/severity/sys-error/exception fields, header logs, implementation-specific logs, and prefix logs. The ESM group defines enhanced capability list fields, ESM headers, status/control bits, and capability registers.

The `BIFPLR3_2` standard PCI/PCIe block maps the bridge-like root-port config space: vendor/device IDs, command/status bits, class code, bus numbers, IO/memory/prefetchable windows, capability pointer, interrupt line/pin, bridge control, PM capability/status-control, PCIe device/link/slot/root capability/control/status fields, and PCIe 2.0 device/link/slot extended capability fields. These macros describe negotiated link speed/width, target speed, retraining controls, ASPM and link disable state, payload/read-request sizes, error-reporting enables, FLR, ARI, AtomicOp, LTR, OBFF, equalization state, slot power/hotplug bits, and root error/status fields.

The `BIFPLR3_2` interrupt and extended capability groups include MSI control/address/data fields, MSI mapping controls, SSID fields, vendor-specific capability headers/data, VC capability/control/status/resource fields, serial-number fields, AER status/mask/severity/log/root-error/source-ID fields, TLP prefix logs, secondary PCIe equalization controls for lanes 0-15, ACS capability/control, multicast controls, L1 PM substate controls, and the DPC enhanced capability list header. The chunk ends immediately before the `BIFPLR3_2_PCIE_DPC_CAP_LIST` field definitions, so DPC capability/control/status detail is expected in the adjacent chunk.

## Control Flow And State

There is no runtime control flow in this slice. The effective flow is compile-time substitution:

1. A translation unit includes `nbio_7_0_sh_mask.h`.
2. Driver code reads or prepares a 16-bit or 32-bit PCI/NBIO register value using a matching address macro from an offset header.
3. The caller applies the generated `*_MASK` and `*_SHIFT` constants to decode or compose an individual field.

The header stores no C state and defines no persistence layer. Persistent state is in the GPU's NBIO PCIe configuration registers and is affected only when code outside this header reads, writes, or clears those registers. Many named fields correspond to hardware state with side effects or externally visible behavior: AER status and masks, root error reporting, VC negotiation, link retraining and equalization, ACS isolation controls, multicast receive/block vectors, L1 PM substate enable/threshold values, DPC control/status, MSI routing, and bridge window configuration.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header convention. The `_sh_mask` header supplies bit positions and masks; sibling offset headers supply register addresses and base indices; `nbio_7_0_default.h` supplies reset/default values for corresponding `smn...` register names. Spot checks show matching default entries for registers such as `smnBIFPLR2_2_PCIE_VC1_RESOURCE_CAP_DEFAULT`, `smnBIFPLR3_2_VENDOR_ID_DEFAULT`, and `smnBIFPLR3_2_PCIE_DPC_ENH_CAP_LIST_DEFAULT`, and matching offset entries are present in related NBIO offset headers.

The file is included by AMDGPU NBIO and SOC paths, including `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `drivers/gpu/drm/amd/amdgpu/soc15.c`, and PowerPlay/SMU support via `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Consumers are expected to use the macros with AMDGPU register access helpers or PCI config-space access paths, not by including this header alone.

The semantic dependencies are the PCI and PCIe specifications for standard configuration headers, PM capability, MSI, PCIe capability, AER, VC, secondary PCIe extended capability/equalization, ACS, multicast, L1 PM substates, DPC, RP PIO, and vendor-specific capability layout. The generated names encode those architectural fields but do not enforce legal combinations or ordering.

## Risks And Maintenance Notes

- The chunk starts mid-register at `BIFPLR2_2_PCIE_VC1_RESOURCE_CAP` and ends at the comment for `BIFPLR3_2_PCIE_DPC_CAP_LIST`; adjacent chunks are required for complete register-family analysis.
- These masks must match the exact NBIO 7.0 hardware definition and the companion offset/default headers. A stale mask can silently corrupt field extraction or program the wrong bit.
- The generated blocks are highly repetitive across `BIFPLR2_2` and `BIFPLR3_2`, especially lane equalization, AER, ACS, VC, multicast, and L1 PM fields. Generation drift is hard to notice in review because the names differ only by port/function prefix or lane number.
- Some status fields are write-one-to-clear or otherwise side-effectful at the hardware level. The presence of a mask does not imply that read-modify-write is safe.
- Control fields for AER, ACS, DPC, VC, MSI, bridge windows, link retraining, equalization, and L1 PM substates can affect isolation, interrupt delivery, error containment, power behavior, and PCIe link stability.
- Masks use C integer constants with `L` suffixes and include full-width values such as `0xFFFFFFFFL`; callers should keep the established AMDGPU register helper types to avoid signedness or truncation surprises.
- Cross-generation comparison shows nearby NBIO generations can change field widths or add fields, so these macros should not be mechanically reused for other NBIO versions without validating the version-specific generated header.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for translation units that include `nbio_7_0_sh_mask.h`, especially `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `smu10_inc.h`.
- Static checks that every field in the slice has a consistent `*_SHIFT`/`*_MASK` pair, that masks are aligned with shifts, and that contiguous multi-bit masks have the expected width.
- Cross-header checks that register names in this chunk have matching address macros in NBIO offset headers and reset/default entries in `nbio_7_0_default.h` where applicable.
- Runtime PCIe config-space validation on NBIO 7.0 hardware: decoded vendor/device IDs, bridge windows, PM state, link speed/width, MSI state, AER masks/status, VC resources, ACS controls, multicast controls, L1 PM substate controls, and DPC capability header should match hardware dumps such as `lspci -vvxxx` and AMDGPU debug register reads.
- Error-path tests that inject or observe AER/DPC/RP PIO conditions and verify the driver decodes, reports, masks, and clears the intended bits without touching unrelated status.
- Link and power-management tests around retrain-link, equalization completion, lane error status, L1.1/L1.2 enablement, common-mode restore time, LTR threshold fields, and wake/PME behavior.

### subset-b-003107: lines 95299-97677

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 95299-97677

## Scope

This chunk covers generated shift and mask macros from the AMD NBIO 7.0 register mask header. It begins inside the `BIFPLR3_2_PCIE_DPC_CAP_LIST` register field definitions, completes the `BIFPLR3_2` Downstream Port Containment, root-port PIO, and ESM capability groups, then enters the `addressBlock: nbio_pcie0_bifplr4_cfgdecp` section. The `BIFPLR4_2` portion covers a root-port/bridge PCI configuration decoder from standard PCI header fields through PCIe capabilities, MSI, vendor-specific capabilities, virtual channels, device serial number, Advanced Error Reporting, secondary PCIe lane equalization, ACS, multicast, L1 PM substates, DPC, root-port PIO diagnostics, and the ESM capability bitmap through part of `PCIE_ESM_CAP_6`.

The file is a generated hardware register bitfield contract. This chunk defines preprocessor constants only. It does not define functions, structs, variables, storage, or executable behavior.

## Purpose

The purpose of this header range is to expose the bit-level ABI for NBIO 7.0 PCIe root-port configuration and diagnostic registers. Each hardware field is represented in the AMD register-header convention:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset.
- `<REGISTER>__<FIELD>_MASK` gives the mask used to extract or compose the field.

Driver code pairs these constants with register offset definitions from the matching NBIO offset header and with AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32`, `WREG32`, or SOC15 register-access wrappers. The constants are not policy by themselves; they are the encoding map that lets runtime code interpret PCIe capability, link, power, isolation, and error-reporting register values correctly.

## Important Macro Families

### BIFPLR3 DPC and Root-Port PIO Tail

The opening part finishes the `BIFPLR3_2` Downstream Port Containment capability group. `BIFPLR3_2_PCIE_DPC_CAP_LIST` advertises DPC interrupt message number, root-port extension support, poisoned-TLP egress blocking support, software-trigger support, RP PIO log size, and data-link-active error-corrected signaling support. `BIFPLR3_2_PCIE_DPC_CNTL` exposes writable containment controls such as trigger enable, completion control, interrupt enable, corrected-error enable, poisoned-TLP egress blocking enable, software trigger, and data-link-active error-corrected enable. `BIFPLR3_2_PCIE_DPC_STATUS` carries containment status, trigger reason, interrupt status, root-port busy state, trigger reason extension, and the first RP PIO error pointer. `BIFPLR3_2_PCIE_DPC_ERROR_SOURCE_ID` contains the source ID associated with a DPC event.

The `BIFPLR3_2_PCIE_RP_PIO_*` registers define root-port PIO completion failure handling. `STATUS`, `MASK`, `SEVERITY`, `SYSERROR`, and `EXCEPTION` share field names for configuration, I/O, and memory unsupported requests, completer aborts, and completion timeouts. Their identical field layout is intentional, but their semantics differ: status reports observed events, mask controls reporting, severity classifies events, sys-error maps events to system error signaling, and exception maps events to exception handling. `HDR_LOG0..3`, `IMPSPEC_LOG`, and `PREFIX_LOG0..3` are whole-dword log registers for captured TLP header, implementation-specific, and TLP prefix information.

### BIFPLR3 ESM Capability

The `BIFPLR3_2_PCIE_ESM_*` group defines an Equalization/ESM-style extended capability block. `CAP_LIST`, `HEADER_1`, and `HEADER_2` provide capability ID, version, next pointer, vendor ID, capability revision, capability length, and nested capability ID fields. `ESM_STATUS` exposes minimum time in EI value and scale fields. `ESM_CTRL` has enable and data-rate selector bits, including Gen3 and Gen4 data-rate controls.

`BIFPLR3_2_PCIE_ESM_CAP_1` through `BIFPLR3_2_PCIE_ESM_CAP_7` are dense bitmaps of supported ESM rates. The naming increments in tenths of GT/s style units, beginning at `ESM_8P0G` and continuing through `ESM_28P0G` by the end of the `BIFPLR3_2` block. Each rate has a one-bit shift and mask. Consumers should treat these as capability bits, not as numeric field values.

### BIFPLR4 Standard PCI Bridge Header

The `addressBlock: nbio_pcie0_bifplr4_cfgdecp` marker introduces a separate root-port bridge instance. `BIFPLR4_2_VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, and `BIST` define the standard PCI configuration header. The `COMMAND` register covers I/O access, memory access, bus mastering, special cycles, memory-write-and-invalidate, VGA palette snoop, parity response, wait-cycle control, SERR enable, fast back-to-back enable, and interrupt disable. `STATUS` reports interrupt state, capability-list presence, 66 MHz support, fast back-to-back capability, parity and abort conditions, DEVSEL timing, and detected parity error.

The bridge routing and aperture registers include `SUB_BUS_NUMBER_LATENCY`, `IO_BASE_LIMIT`, `SECONDARY_STATUS`, `MEM_BASE_LIMIT`, `PREF_BASE_LIMIT`, `PREF_BASE_UPPER`, `PREF_LIMIT_UPPER`, and `IO_BASE_LIMIT_HI`. These encode primary/secondary/subordinate bus numbers, secondary latency timer, I/O base and limit, memory base and limit, and 64-bit prefetchable memory range bounds. A wrong bitfield in these macros would affect PCI enumeration and downstream address decoding.

`CAP_PTR`, `INTERRUPT_LINE`, `INTERRUPT_PIN`, `IRQ_BRIDGE_CNTL`, and `EXT_BRIDGE_CNTL` complete the bridge header. Bridge-control fields cover parity response, SERR, ISA/VGA routing, VGA 16-bit decode, secondary bus reset, fast back-to-back enable, and discard timer/error controls. The extended bridge control includes the port-80 enable bit used by platform routing/debug behavior.

### Power Management and Base PCIe Capability

`BIFPLR4_2_PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` define the PCI Power Management capability. They cover capability list linkage, PM version, PME clock, device-specific initialization, auxiliary current, D1/D2 support, PME support bitmap, current power state, no-soft-reset, PME enable/status, data select/scale, B2/B3 support, bus power/clock control enable, and PM data.

`BIFPLR4_2_PCIE_CAP_LIST` and `PCIE_CAP` expose the PCIe capability header, device type, slot-implemented bit, and interrupt message number. `DEVICE_CAP`, `DEVICE_CNTL`, and `DEVICE_STATUS` describe and control endpoint/root-port PCIe behavior: maximum payload, phantom functions, extended tags, L0s/L1 latency, role-based error reporting, function-level reset, error-reporting enables, relaxed ordering, max payload size, extended tag enable, phantom function enable, auxiliary PM, no-snoop, max read request, bridge configuration retry enable, corrected/nonfatal/fatal/unsupported-request status, AUX power, and transaction-pending state.

`LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS` cover PCIe link advertisement and live state. Important fields include supported link speeds, maximum link width, ASPM support and control, L0s/L1 exit latency, clock power management, surprise-down reporting, data-link-layer active reporting, bandwidth notification support, port number, read completion boundary, link disable, retrain, common clock configuration, extended sync, hardware autonomous width disable, bandwidth interrupt enables, current link speed and width, link training, slot clock configuration, data-link-layer active, and bandwidth-management status.

### Slot, Root, Capability 2, and MSI

`SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS` map hotplug and slot-management fields, including attention button, power controller, MRL sensor, attention/power indicators, hotplug surprise and capability bits, slot power limit and scale, interlock, command completed support, physical slot number, event enables, indicator controls, power control, electromechanical interlock control, data-link-state change enable, and presence/interlock/data-link-change status bits.

`ROOT_CNTL`, `ROOT_CAP`, and `ROOT_STATUS` define root-port error and PME handling: SERR on correctable/nonfatal/fatal errors, PME interrupt enable, CRS software visibility, PME requestor ID, PME status, and PME pending.

`DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2` cover second-generation PCIe features. These include completion timeout ranges and controls, ARI forwarding, atomic-op routing and blocking, ID-based ordering, LTR, TPH completer support, OBFF, extended format and end-to-end TLP prefix support, emergency power reduction, 10-bit tags, lower SKP OS generation, target link speed, compliance mode, hardware autonomous speed disable, selectable de-emphasis, transmit margin, enter modified compliance, compliance SOS, equalization controls and phase-success bits, current de-emphasis level, retimer presence, emergency power reduction initialization, and associated status flags.

The MSI and subsystem groups are `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MSG_DATA_64`, `SSID_CAP_LIST`, and `SSID_CAP`. They provide MSI enablement, multiple-message capability and enable fields, 64-bit address capability, per-vector masking support, MSI address/data payloads, and subsystem vendor/device IDs. `MSI_MAP_*` maps MSI translation capability and address registers.

### Vendor-Specific, Virtual Channel, Serial Number, and AER

`BIFPLR4_2_PCIE_VENDOR_SPECIFIC_*` defines a PCIe vendor-specific extended capability list entry, vendor-specific header fields, and two vendor-specific data dwords. `PCIE_VC_*`, `PCIE_PORT_VC_*`, and `PCIE_VC0/VC1_RESOURCE_*` define virtual-channel capability, arbitration, status, traffic class mapping, VC IDs, VC enable state, load table controls, arbitration selection, negotiation pending, and table status fields.

`PCIE_DEV_SERIAL_NUM_ENH_CAP_LIST`, `PCIE_DEV_SERIAL_NUM_DW1`, and `PCIE_DEV_SERIAL_NUM_DW2` expose the device serial number capability and two 32-bit serial-number dwords.

`PCIE_ADV_ERR_RPT_ENH_CAP_LIST` starts Advanced Error Reporting. `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` share uncorrectable error fields for data link protocol error, surprise down, poisoned TLP, flow control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC error, unsupported request, ACS violation, uncorrectable internal error, multicast blocked TLP, atomic-op egress blocked, TLP prefix blocked, and poisoned-TLP egress blocked. `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover receiver error, bad TLP, bad DLLP, replay rollover, replay timer timeout, advisory nonfatal, correctable internal error, and header-log overflow.

`PCIE_ADV_ERR_CAP_CNTL` provides first-error pointer, ECRC generation/check capability and enables, multiple header recording, and TLP prefix log presence. `PCIE_HDR_LOG0..3` and `PCIE_TLP_PREFIX_LOG0..3` are full 32-bit captured log dwords. `PCIE_ROOT_ERR_CMD`, `PCIE_ROOT_ERR_STATUS`, and `PCIE_ERR_SRC_ID` define root-port AER reporting enable bits, received and multiple error status, first uncorrectable fatal classification, advanced error interrupt message number, and correctable/uncorrectable source IDs.

### Secondary PCIe, Equalization, ACS, Multicast, and L1 PM

`PCIE_SECONDARY_ENH_CAP_LIST`, `PCIE_LINK_CNTL3`, and `PCIE_LANE_ERROR_STATUS` define the secondary PCIe extended capability and lane-error bitmap. `PCIE_LANE_0_EQUALIZATION_CNTL` through `PCIE_LANE_15_EQUALIZATION_CNTL` repeat the same four fields per lane: downstream port transmitter preset, downstream port receiver preset hint, upstream port transmitter preset, and upstream port receiver preset hint. This regularity is important for code that iterates over lanes during equalization or diagnostics.

`PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` define Access Control Services fields: source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, enhanced capability, and egress control vector size. These fields integrate with peer-to-peer routing and isolation policy.

`PCIE_MC_ENH_CAP_LIST`, `PCIE_MC_CAP`, `PCIE_MC_CNTL`, `PCIE_MC_ADDR0/1`, `PCIE_MC_RCV0/1`, `PCIE_MC_BLOCK_ALL0/1`, `PCIE_MC_BLOCK_UNTRANSLATED_0/1`, and `PCIE_MC_OVERLAY_BAR0/1` define the PCIe multicast capability. They include multicast group count, multicast enable, base address, receive masks, block-all masks, untranslated-block masks, and overlay BAR size/address fields.

`PCIE_L1_PM_SUB_CAP_LIST`, `PCIE_L1_PM_SUB_CAP`, `PCIE_L1_PM_SUB_CNTL`, and `PCIE_L1_PM_SUB_CNTL2` define L1 PM substate support and controls. The fields cover PCI-PM L1.2/L1.1 support, ASPM L1.2/L1.1 support, L1 PM substate support, common-mode restore time, power-on scale/value, L1.2/L1.1 enable bits, LTR L1.2 threshold value/scale, and T_POWER_ON timing controls.

### BIFPLR4 DPC, RP PIO, and ESM

`BIFPLR4_2_PCIE_DPC_ENH_CAP_LIST`, `DPC_CAP_LIST`, `DPC_CNTL`, `DPC_STATUS`, and `DPC_ERROR_SOURCE_ID` mirror the `BIFPLR3_2` DPC layout for this root-port instance. These fields control and report containment behavior for severe downstream PCIe errors.

`BIFPLR4_2_PCIE_RP_PIO_STATUS`, `MASK`, `SEVERITY`, `SYSERROR`, and `EXCEPTION` repeat the same config/I/O/memory unsupported-request, completer-abort, and completion-timeout fields used by `BIFPLR3_2`. `HDR_LOG0..3`, `IMPSPEC_LOG`, and `PREFIX_LOG0..3` again expose captured TLP context as whole-register dwords.

The final section defines `BIFPLR4_2_PCIE_ESM_*`. `CAP_LIST`, `HEADER_1`, `HEADER_2`, `STATUS`, and `CTRL` provide ESM capability metadata, minimum time-in-EI fields, and enable/data-rate controls. `ESM_CAP_1` through the covered portion of `ESM_CAP_6` provide one-bit capability entries from `ESM_8P0G` through `ESM_24P4G`. The adjacent following chunk continues the remaining `ESM_CAP_6` masks and later ESM capability registers.

## Control Flow

There is no runtime control flow in this header chunk. The only structure is generated ordering: register comments followed by `#define` constants for shifts and masks. Runtime control flow lives in code that includes this header and decides when to read, write, or decode the associated PCIe/NBIO registers.

The implicit access pattern for writable fields is read-modify-write: read the register, clear a field using its mask, shift the desired value by the field's `__SHIFT`, apply the mask, and write the composed value. For status and log registers, consumers typically read and decode the field, then clear or preserve it according to hardware access rules that are not encoded in this file.

## State and Persistence Behavior

The macros are compile-time constants and have no state or persistence. The hardware registers they describe represent several state classes:

- Configuration identity and capability advertisement, such as vendor/device IDs, class codes, PCIe capability headers, serial number, ACS capability, DPC capability, ESM capability, and multicast capability.
- Writable policy and control state, including PCI command bits, bridge apertures, MSI enable and message fields, device/link/slot/root controls, VC controls, ACS controls, multicast controls, L1 PM controls, DPC controls, AER masks/severity, and ESM controls.
- Volatile status state, including link training, negotiated speed/width, slot events, root PME state, AER status, DPC trigger and busy state, RP PIO status, secondary lane error status, and ESM status.
- Diagnostic capture state, including AER TLP header/prefix logs, RP PIO TLP header/prefix logs, implementation-specific PIO logs, DPC error source ID, and AER source ID.

Resets, secondary bus reset, link retraining, power-state transitions, firmware reinitialization, DPC containment, and hardware error events can change the backing register values. This header does not describe reset values; those are kept in matching generated default headers.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.0 register-address headers for the corresponding `BIFPLR3_2` and `BIFPLR4_2` registers. The mask names are useful only when paired with the matching register address and the correct root-port instance. Other generated files in the same directory provide default values and offsets; newer NBIO variants may have similar names but not identical fields.

Important integration areas include:

- PCI enumeration and bridge-resource setup using command/status, bus number, I/O window, memory window, and prefetchable window fields.
- PCIe link management using link capability/control/status, Link Control 2/3, lane error status, per-lane equalization controls, and ESM rate capability/control fields.
- Power management using PMI fields and L1 PM substate support/timing/control fields.
- Interrupt and message setup using MSI capability, MSI mapping, root error command/status, DPC interrupt fields, and advanced-error interrupt message number fields.
- Error handling and diagnostics using AER status/mask/severity, header and prefix logs, DPC status/source ID, RP PIO status/mask/severity/sys-error/exception, and PIO logs.
- Isolation and routing policy using ACS, virtual channels, ARI-adjacent capability data from neighboring chunks, and multicast capability/control registers.
- Hotplug and root-port service paths using slot capability/control/status and root PME/error fields.

## Risks

The primary risk is bitfield drift from the hardware specification or generated register database. Incorrect shifts or masks can silently corrupt read-modify-write operations or misdecode hardware state. The highest-risk fields are writable controls and error/security policy bits: bridge aperture fields, bus-master and memory-enable bits, AER masks/severity, DPC controls, ACS controls, multicast routing bits, L1 PM controls, link retrain/disable controls, and per-lane equalization presets.

The repeated naming is another risk. `BIFPLR3_2` and `BIFPLR4_2` contain many identical field names with different register prefixes. Accidentally using a macro from the wrong root-port prefix can compile cleanly while addressing the wrong port's register layout. The same issue applies across NBIO versions such as `nbio_7_0` and `nbio_7_7_0`, where similar blocks may gain or lose fields.

Several registers intentionally have confusing names such as `*_MASK__*_MASK_MASK`, because the register is itself a mask register and the field is also named `MASK`. Automated cleanup should not simplify these names. Status, mask, severity, sys-error, and exception registers often share identical field names but have different write/read semantics.

Whole-register log fields use shift zero and `0xFFFFFFFFL` masks. They should be treated as raw captured dwords, not as packed subfields defined by this header. Conversely, multi-bit fields such as link speed, link width, bridge apertures, slot power limit, completion timeout, equalization presets, LTR thresholds, and ESM status fields require both the mask and shift; testing only single-bit flags would miss width or offset errors.

This chunk ends mid-register in `BIFPLR4_2_PCIE_ESM_CAP_6`: it includes all shifts and masks only through `ESM_24P4G_MASK`. Merge/reconciliation must combine it with the adjacent chunk before making whole-register statements about `ESM_CAP_6`.

## Test Signals

Useful validation signals for this chunk are mostly generated-header and hardware integration checks:

- Kernel or AMDGPU build coverage that includes this header and catches missing or renamed macros.
- Static checks that each field has a matching `__SHIFT` and `_MASK` entry, with special attention to the chunk boundary in `BIFPLR4_2_PCIE_ESM_CAP_6`.
- Diffs against the authoritative NBIO 7.0 register source for all `BIFPLR3_2` and `BIFPLR4_2` fields in this range.
- PCIe enumeration tests on NBIO 7.0 hardware validating bridge identity, bus numbers, memory/I/O apertures, MSI capability, link capability, slot/root capability, and subsystem IDs.
- Link-management and power-management tests covering negotiated link speed/width, link retrain, equalization presets, ESM capability decode, ASPM/L1 substates, and resume latency.
- AER/DPC fault-injection or observation tests confirming uncorrectable/correctable error status, masks, severity, source IDs, TLP logs, DPC trigger/status/source ID, and RP PIO logs decode correctly.
- Isolation/routing tests for ACS, virtual channels, multicast, and peer-to-peer scenarios, especially where IOMMU, hotplug, or multi-function routing behavior depends on these fields.

### subset-b-003108: lines 97678-100078

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 97678-100078

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,181 `#define` macros and 216 register/address-block comments. There are no functions, structs, enums, globals, locks, allocations, or executable statements in this range.

The range starts at the tail of `BIFPLR4_2_PCIE_ESM_CAP_6`, covers `BIFPLR4_2_PCIE_ESM_CAP_7`, then the full `nbio_pcie0_bifplr5_cfgdecp` PCI/PCIe bridge configuration-decode block, and ends partway through the next `nbio_pcie0_bifplr6_cfgdecp` block at `BIFPLR6_2_DEVICE_CNTL2`. Adjacent chunks are needed for the beginning of `BIFPLR4_2_PCIE_ESM_CAP_6` and the remainder of `BIFPLR6_2`.

Although this source mirror lives under `sources/distributed-fs/ceph-client`, the file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield-layout half of AMD's generated NBIO 7.0 register interface. For every hardware register field it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used to encode or decode the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, preserve, clear, or compose that field.

This chunk describes PCI Express bridge configuration-space fields for the NBIO `BIFPLR*_2` root-port instances. The covered registers include conventional PCI bridge header fields, PCI power-management capability fields, PCIe capability/device/link/slot/root fields, MSI and subsystem-ID fields, vendor-specific and virtual-channel enhanced capabilities, device serial number, Advanced Error Reporting, secondary PCIe link/equalization controls, Access Control Services, multicast, L1 PM substates, Downstream Port Containment, Root Port PIO logging, and the PCIe ESM capability bitmaps. These constants let AMDGPU code decode or compose register words without hard-coding bit positions at call sites.

## Important Macro Families

The opening `BIFPLR4_2_PCIE_ESM_CAP_7` section completes the previous port's ESM-speed capability bitmap. It maps one-bit ESM capability flags from `ESM_25P0G` through `ESM_28P0G`; the first five lines in the chunk are the closing masks for `BIFPLR4_2_PCIE_ESM_CAP_6`.

The `BIFPLR5_2` block is complete in this chunk and covers a full PCIe bridge/root-port configuration layout:

- Base PCI bridge identification and decode fields: vendor/device ID, command/status bits, revision/class codes, header/BIST, bus numbering, IO and memory windows, prefetchable base/limit upper words, capability pointer, interrupt line/pin, bridge control, and an AMD extension for port-80 IO decode.
- Power-management capability fields: capability-list IDs and next pointers, PM version, PME clock/support, D1/D2 support, power-state selection, PME enable/status, data select/scale, B2/B3 support, bus-power enable, and PM data.
- PCIe capability fields: device type, slot implemented, interrupt message number, maximum payload/read request sizing, extended tag, relaxed/no-snoop ordering, function-level reset capability, completion timeout, ARI forwarding, atomic operations, ID-based ordering, LTR, OBFF, end-to-end TLP prefix support, and link/slot/root controls and statuses.
- MSI and identification capabilities: MSI enable/multiple-message controls, 32/64-bit message address/data fields, subsystem/vendor IDs, and MSI map capability/address registers.
- Enhanced capabilities: vendor-specific headers/data words, virtual channel port/resource controls, device serial number, Advanced Error Reporting status/mask/severity/header logs/root error reporting/source IDs/TLP prefix logs, secondary PCIe link/equalization controls for lanes 0-15, ACS capability/control, multicast capability/control/address/receive/block/overlay registers, L1 PM substate capabilities and controls, DPC capability/control/status/error source, Root Port PIO status/mask/severity/system-error/exception/header-log/implementation-specific/prefix-log fields, and ESM capability/status/control/capability bitmap registers.

The `BIFPLR6_2` block begins the next root-port instance with the same generated pattern. This chunk includes its base PCI bridge fields, PM capability, first-generation PCIe capability, link/slot/root controls and statuses, and `DEVICE_CAP2`/the beginning of `DEVICE_CNTL2`. The remaining `BIFPLR6_2` fields are outside this chunk.

## APIs, Types, And Functions

There are no callable APIs or C types in this range. The public interface is the generated preprocessor namespace. The macro values are untyped integer literals, mostly with an `L` suffix, and encode only field geometry.

These definitions do not include register addresses, reset values, access size, read/write permissions, write-one-to-clear behavior, hardware sequencing rules, firmware ownership, or side effects. Consumers must combine them with the matching generated address/default metadata and AMDGPU register helpers such as `REG_GET_FIELD`, `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, or the NBIO/SMN/PCIe access path appropriate for the target register.

## Control Flow

This header has no local runtime control flow. Runtime behavior is external:

1. AMDGPU or platform code selects a `BIFPLR*_2_*` register address from sibling generated NBIO metadata.
2. Code reads a hardware register and decodes fields with the `__SHIFT` and `_MASK` constants, or composes an updated value while preserving unrelated and reserved bits.
3. The decoded or programmed values participate in PCIe root-port setup, link negotiation, power management, error reporting, interrupt delivery, link equalization, containment, or diagnostic reporting.

Several fields represent asynchronous hardware/protocol state rather than ordinary software state: link training and data-link-active bits, PME status/pending/requestor IDs, hotplug/slot status bits, AER/DPC/Root Port PIO error latches and logs, VC negotiation/pending flags, L1 substate controls, lane error and equalization state, and ESM status/control bits.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO PCIe bridge/root-port configuration registers. Persistence depends on the GPU reset domain, PCIe conventional reset, link reset/retrain, power management, firmware/BIOS setup, suspend/resume restore, and explicit AMDGPU writes.

Represented state includes writable control bits, capability readbacks, bus/window decode values, MSI routing values, interrupt controls, power-management settings, link width/speed negotiation status, slot/hotplug state, error masks/severities/status latches, header/TLP-prefix logs, equalization settings, ACS/multicast policies, DPC containment state, Root Port PIO diagnostics, and ESM capability bitmaps. Some fields are likely read-only capability/status values, some are write-one-to-clear status bits, and some are writable policy controls; that access behavior is not encoded by the shift/mask macros alone.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.0 register database and must stay synchronized with sibling generated headers:

- `nbio_7_0_offset.h` and `nbio_7_0_smn.h` provide address metadata for the same NBIO register set.
- `nbio_7_0_default.h` provides reset/default values for many matching registers.
- AMDGPU SOC15/NBIO register access helpers and bitfield helper macros apply these shifts and masks at runtime.

Integration points include AMDGPU NBIO initialization, PCIe root-port configuration, GPU reset and resume restore, ASPM/L1 PM substate handling, MSI programming, AER/DPC error handling, hotplug/slot status reporting, virtualization/IOMMU-facing ACS policy, multicast/VC configuration, and low-level PCIe diagnostics. The `BIFPLR5_2` and `BIFPLR6_2` naming indicates repeated mechanically generated per-port instances, so consumers must select the instance that matches the active hardware port.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while causing code to write the wrong PCIe configuration bit, producing link, enumeration, interrupt, power-management, or error-reporting failures.
- The chunk starts and ends in the middle of register families. Whole-file research must reconcile the preceding `BIFPLR4_2_PCIE_ESM_CAP_6` fields and following `BIFPLR6_2` fields before treating either boundary register set as complete.
- Many status fields in PCIe/AER/DPC/slot/root-port registers have protocol-specific clearing semantics. The shift/mask header does not identify write-one-to-clear or read-only fields, so call sites must rely on hardware documentation and existing helpers.
- Link and power-management controls can trigger asynchronous state transitions. Writers must handle link-training timeouts, device removal, reset races, PME races, and non-converging equalization or DPC recovery.
- PCI bridge window, bus-number, ACS, multicast, and VC fields affect traffic routing and isolation. Incorrect programming can break enumeration, DMA reachability, peer-to-peer routing, or virtualization isolation.
- MSI address/data and MSI-map fields are interrupt-routing sensitive; stale restore values or wrong masks can misroute interrupts.
- AER/DPC and Root Port PIO logs can be lost or corrupted if status bits are cleared before software captures the associated header/source/prefix fields.
- The `BIFPLR5_2` and `BIFPLR6_2` definitions repeat the same layout for different ports. Copy/paste or generator mistakes can affect one port instance only, making failures topology-dependent.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing or renamed generated symbols referenced by consumers.
- Run generated-header consistency checks: every `__SHIFT` should have a compatible `_MASK`, masks should not overlap unexpectedly within a register, and repeated `BIFPLR*_2` port instances should match where hardware layout is intended to be identical.
- Cross-check this chunk against `nbio_7_0_offset.h`, `nbio_7_0_smn.h`, and `nbio_7_0_default.h` so each field layout maps to a known register address and expected default where one exists.
- On supported hardware, validate PCIe enumeration, bus/window decoding, negotiated link speed/width, link retraining, ASPM/L1 substate transitions, GPU reset, and suspend/resume.
- Exercise interrupt and error paths: MSI delivery, PME signaling, AER correctable/nonfatal/fatal reporting, DPC trigger/recovery, Root Port PIO status/log capture, hotplug/slot status changes, and lane error/equalization status readback.
- For any code that writes these fields, inspect register traces to ensure reserved bits are preserved, status/log fields are cleared only after capture, and per-port writes target the expected `BIFPLR5_2` or `BIFPLR6_2` instance.

### subset-b-003109: lines 100079-102486

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 100079-102486

## Scope

This chunk is a generated AMD NBIO 7.0 shift/mask header segment. It contains C preprocessor constants only; there are no functions, structs, variables, branches, loops, allocations, locks, or direct register accesses in this range.

The slice contains 2,161 `#define` entries, split almost exactly into paired field definitions: 1,081 `__SHIFT` macros and 1,080 `_MASK` macros. It starts inside the tail of `BIFPLR6_2_DEVICE_CNTL2`, with only the last four mask constants for IDO completion, LTR, OBFF, and end-to-end TLP prefix blocking. It then covers the remainder of the `BIFPLR6_2` PCIe capability and extended-capability layout, a small `NB_PCIEDUMMY1_2` dummy PCI configuration block, and most of the `BIF_CFG_DEV0_RC2` root-complex configuration-space layout through lane 7 equalization control shifts. The final `BIF_CFG_DEV0_RC2_PCIE_LANE_7_EQUALIZATION_CNTL` masks continue after this chunk.

Although this file is under a local `ceph-client` source mirror, the content is AMDGPU hardware metadata for GPU NBIO/BIF PCIe configuration space. It does not implement Ceph or distributed filesystem behavior.

## Purpose

The purpose of this range is to publish bit positions and bit masks for NBIO 7.0 PCIe bridge/root-port and root-complex register fields. Each field is represented by generated macro pairs:

- `<REGISTER>__<FIELD>__SHIFT`, the bit offset used when extracting or composing a field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or set a field.

Runtime code combines these constants with matching generated offset and default headers, plus AMDGPU register helpers such as `RREG32`, `WREG32`, `RREG32_PCIE`, `WREG32_PCIE`, `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_GET_FIELD`, and `REG_SET_FIELD`. The header itself does not know whether a register is read-only, write-one-to-clear, sticky, side-effecting, or owned by firmware, hardware, Linux PCI core policy, or the AMDGPU driver.

## Important Macro Families

The opening `BIFPLR6_2` tail completes `DEVICE_CNTL2` masks and then defines PCIe Capability 2 fields: `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, and slot capability/control/status 2 placeholders. These cover completion-timeout, ARI, atomic-op, IDO, LTR, OBFF, TLP-prefix, supported link speed, compliance, de-emphasis, transmit margin, and link equalization status/control semantics for the BIFPLR6_2 port.

The `BIFPLR6_2` MSI and subsystem sections define standard MSI capability list linkage, MSI enable and multiple-message controls, 64-bit capability and per-vector masking capability bits, MSI message address/data fields, subsystem vendor/device ID fields, and MSI map capability/address fields.

The `BIFPLR6_2` vendor-specific, virtual-channel, and device-serial-number sections describe PCIe extended capability headers, VSEC metadata, scratch payload dwords, virtual-channel capability/control/status registers, VC0/VC1 resource capability/control/status fields, and serial-number dwords. These constants define the visible PCIe extended-capability layout but not the reset values or which capabilities are actually enabled on a given device instance.

The `BIFPLR6_2` Advanced Error Reporting section is extensive. It defines AER enhanced capability linkage, uncorrectable error status/mask/severity fields, correctable error status/mask fields, advanced error capability/control bits, four TLP header log dwords, root error command/status fields, error source IDs, and four TLP prefix log dwords. Covered error categories include data-link protocol errors, surprise down, poisoned TLP, flow-control protocol errors, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, atomic-op egress blocked, and TLP-prefix blocked. Correctable fields include receiver error, bad TLP, bad DLLP, replay rollover, replay timer timeout, advisory non-fatal error, correctable internal error, and header-log overflow.

The `BIFPLR6_2` secondary PCIe and lane-training section includes Link Control 3, lane error status, and per-lane equalization controls for lanes 0 through 15. Each lane control register has downstream TX preset, downstream RX preset hint, upstream TX preset, upstream RX preset hint, and reserved fields.

The later `BIFPLR6_2` extended-capability groups cover Access Control Services, multicast, L1 PM substates, Downstream Port Containment, Root Port PIO error reporting, and ESM metadata. These include ACS capability/control bits such as source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress-vector size. Multicast fields include MC max group, window size, ECRC regeneration support, enable controls, group and BAR indexes, receive/block-all/block-untranslated bitmaps, and overlay BAR fields. L1 PM substates cover ASPM L1.1/L1.2 and PCI-PM L1.1/L1.2 support/enables plus timing fields. DPC fields cover containment capability, trigger reason, interrupt/message controls, status bits, and source IDs. RP PIO fields cover status, mask, severity, system-error, exception, header logs, implementation-specific log, and prefix logs. ESM `CAP_1` through `CAP_7` are large generated bitfields for ESM capability payloads.

The `NB_PCIEDUMMY1_2` block is a small dummy PCI configuration decode block. It defines device/vendor ID, command/status, class-code/revision, header type, and a writeable header-type view. This appears as a generated placeholder or dummy PCI function view rather than a full PCIe root-port capability chain.

The `BIF_CFG_DEV0_RC2` block begins at `addressBlock: nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` and defines a root-complex or root-port PCI configuration image. It includes standard PCI identity and bridge header fields, bus numbering, I/O/memory/prefetchable windows, capability pointer, interrupt pins, bridge controls, power-management capability/control, PCIe root-port capability registers, MSI and subsystem fields, MSI map fields, VSEC, VC resources, serial number, AER, root error reporting, secondary PCIe link controls, lane error status, and lane equalization controls for lanes 0 through 7. The chunk ends after the lane 7 shift definitions; the corresponding lane 7 masks are outside this work item.

## APIs, Types, And Functions

There are no callable APIs, C types, or functions in this chunk. The exported interface is the macro namespace itself:

- `BIFPLR6_2_*__SHIFT` and `BIFPLR6_2_*_MASK` for one NBIO 7.0 BIF/PCIe port capability map.
- `NB_PCIEDUMMY1_2_*__SHIFT` and `NB_PCIEDUMMY1_2_*_MASK` for the dummy PCI configuration decode block.
- `BIF_CFG_DEV0_RC2_*__SHIFT` and `BIF_CFG_DEV0_RC2_*_MASK` for the device 0 root-complex/root-port PCI configuration map.

Direct in-tree include sites for the NBIO 7.0 generated header set include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/soc15.c`, and the SMU10 PowerPlay include aggregator at `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`. Display resource code includes the sibling NBIO 7.0 offset header for related register addressing.

## Control Flow

This header has no executable control flow. Runtime control flow appears only in consumers:

1. AMDGPU code selects an NBIO 7.0 register offset or SMN/config-space address from the generated address database.
2. It reads a register through the SOC15, PCIe, MMIO, or indirect register access helpers.
3. It decodes or composes fields with the relevant `__SHIFT` and `_MASK` constants, often through `REG_GET_FIELD` or `REG_SET_FIELD`.
4. It writes updated control values, reports status, preserves reserved bits, clears sticky status where appropriate, or compares observed state against generated defaults and driver policy.

For this chunk, likely runtime contexts include PCIe root-port capability discovery, link training and equalization diagnostics, PCIe power-management policy, MSI programming, AER/RAS diagnostics, DPC containment handling, bridge window configuration, root error reporting, ACS/multicast capability exposure, and platform initialization or restore flows in `nbio_v7_0.c` and `soc15.c`.

## State And Persistence Behavior

The header stores no software state and persists nothing. It describes hardware-backed and configuration-space-backed state owned by NBIO, the PCIe fabric, platform firmware, Linux PCI core policy, and AMDGPU runtime code.

The represented state includes static capabilities, programmable controls, hardware-updated status bits, interrupt routing state, bridge resource windows, PCIe link negotiation state, lane equalization presets and hints, AER masks/severities/logs, DPC status, L1 substate policy, ACS controls, multicast windows, and root-port PIO diagnostics. Some fields are software-programmed controls, some are capability declarations, some are hardware status, and some error/log fields may be sticky or write-one-to-clear in the underlying hardware. The macros do not encode access permissions, reset defaults, ownership, timing, ordering, or side effects.

The sibling `nbio_7_0_default.h` supplies reset/default values for the same generated namespaces. In this chunk's range, examples include nonzero defaults for `BIFPLR6_2_PCIE_CAP_LIST`, `DEVICE_CNTL`, `LINK_CAP`, `LINK_STATUS`, `LINK_CAP2`, `LINK_CNTL2`, MSI and enhanced-capability list headers, VC resource status/control, AER masks/severities, lane equalization controls, RP PIO mask, `NB_PCIEDUMMY1_2_HEADER_TYPE`, and `BIF_CFG_DEV0_RC2_INTERRUPT_LINE`, `INTERRUPT_PIN`, `PCIE_CAP`, `LINK_STATUS`, MSI message control, AER capability defaults, and lane equalization controls. These defaults must stay aligned with this shift/mask layout but are intentionally kept in a separate generated header.

## Dependencies And Integration Points

The main dependencies are the other generated NBIO 7.0 hardware metadata files:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h` for matching register offsets and address constants.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h` for reset/default values.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_smn.h` for related SMN address definitions.

Important AMDGPU integration points are `nbio_v7_0.c` for NBIO 7.0 setup, doorbell aperture handling, PCIe/NBIO clock-gating and light-sleep handling, IH control, and memory-controller access gating; `soc15.c` for SOC15 device initialization and IP wiring; SMU10 PowerPlay include paths for power-management code that needs the generated register database; and display resource code that references NBIO offset state.

External integration surfaces include Linux PCI enumeration, root-port bridge setup, PCIe AER and DPC handling, MSI interrupt delivery, IOMMU and address-routing policy, firmware-owned PCIe configuration, platform power management, suspend/resume restore, GPU reset flows, and diagnostics that dump or decode PCIe configuration space.

## Risks And Edge Cases

- Chunk boundaries are artificial. The first line is already inside `BIFPLR6_2_DEVICE_CNTL2` masks, and the final lines contain only `BIF_CFG_DEV0_RC2_PCIE_LANE_7_EQUALIZATION_CNTL` shifts without the matching masks.
- The macros are untyped preprocessor constants. A wrong mask, stale shift, or copied register prefix can compile cleanly while decoding or programming the wrong hardware field.
- Similar PCIe capability blocks repeat across `BIFPLR6_2` and `BIF_CFG_DEV0_RC2`. Consumers must pair masks with the offset namespace for the same block and NBIO generation.
- PCIe Device Control, Device Control 2, Link Control, Link Control 2, Link Control 3, and lane equalization fields are interoperability-sensitive. Incorrect payload size, read request size, relaxed ordering, no-snoop, completion timeout, ARI, atomic-op, IDO, LTR, OBFF, TLP-prefix, target speed, retrain, compliance, de-emphasis, transmit margin, or equalization programming can break DMA, ordering, enumeration, link stability, reset, or power behavior.
- Bridge header and window fields in `BIF_CFG_DEV0_RC2` affect bus numbering and I/O/memory/prefetchable resource exposure. Bad masks or mismatched offsets can confuse PCI bridge resource assignment.
- MSI fields control interrupt delivery. Mistakes in MSI enable, multiple-message, 64-bit capability, address, data, mask, or mapping fields can cause lost, duplicated, or misrouted interrupts.
- AER and RP PIO status/log fields may be sticky or clear-on-write. Treating them as ordinary read/modify/write storage can erase diagnostic evidence or leave errors masked or misclassified.
- ACS fields affect peer-to-peer routing and isolation. Incorrect source validation, redirect, upstream forwarding, egress control, or translated P2P handling can create security or correctness issues in multi-device and virtualized configurations.
- L1 PM substate and OBFF/LTR fields interact with platform power policy. Enabling unsupported combinations can produce latency spikes, wake issues, or link instability.
- DPC fields control containment and interrupt reporting for downstream-port errors. Incorrect control/status handling can hide fatal link events or leave a port contained.
- Generated defaults are separate from masks. Code that assumes a zero reset value from the presence of a zero-based shift will miss nonzero defaults in `nbio_7_0_default.h`.

## Test Signals

Useful validation is mostly build-time generated-header consistency plus hardware and platform integration testing:

- Build AMDGPU with NBIO 7.0/SOC15/SMU10 paths enabled so missing, renamed, or malformed macros surface in `nbio_v7_0.c`, `soc15.c`, and PowerPlay include chains.
- Run generated-header consistency checks that every complete register marker in this chunk has expected paired `__SHIFT` and `_MASK` definitions, except for the intentional chunk-boundary cases at the opening `DEVICE_CNTL2` tail and closing `LANE_7_EQUALIZATION_CNTL` shifts.
- Compare the `BIFPLR6_2`, `NB_PCIEDUMMY1_2`, and `BIF_CFG_DEV0_RC2` register names against `nbio_7_0_default.h` to confirm reset/default rows remain synchronized with this layout.
- On NBIO 7.0 hardware, inspect PCIe root-port and BIF configuration dumps for capability-chain discovery, MSI capability exposure, VSEC/VC/serial-number headers, AER registers, ACS, multicast, L1 PM substates, DPC, RP PIO, ESM, and lane equalization fields.
- Exercise PCIe link speed changes, retraining, suspend/resume, runtime power transitions, and bandwidth/equalization diagnostics while checking Link Status, Link Status 2, Link Control 2/3, lane error status, and per-lane preset fields.
- Use PCIe AER or platform error injection where available to verify uncorrectable/correctable status, masks, severity, first-error pointer, header logs, TLP prefix logs, root error command/status, error source IDs, DPC status, and RP PIO logs decode correctly.
- Stress MSI delivery under graphics, compute, interrupt-heavy, reset, and power-transition workloads to catch message-control/address/data/map regressions.
- Validate PCI bridge resource assignment and enumeration after cold boot, warm reboot, GPU reset, and resume, especially bus-number, I/O, memory, prefetchable, command/status, and bridge-control fields.
- In systems using ACS, multicast, or strict IOMMU isolation, validate peer-to-peer routing and isolation policy before and after reset and power transitions.

## Chunk Notes

- Lines 100079-100082 finish only the mask half of `BIFPLR6_2_DEVICE_CNTL2`; its field shifts and earlier masks are in the previous chunk.
- Lines 100083-101435 cover the remainder of the `BIFPLR6_2` capability and extended-capability map from `DEVICE_STATUS2` through ESM `CAP_7`.
- Lines 101436-101461 define `addressBlock: nbio_iohub_nb_pciedummy1_pciedummy_cfgdec` and the compact `NB_PCIEDUMMY1_2` dummy PCI config block.
- Lines 101462-102480 define `addressBlock: nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` from root-complex identity/header fields through lane 6 equalization control.
- Lines 102481-102486 begin `BIF_CFG_DEV0_RC2_PCIE_LANE_7_EQUALIZATION_CNTL` and include only its shift definitions; the matching masks are in the following chunk.

### subset-b-003110: lines 102487-104918

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 102487-104918

## Scope

This chunk covers 2,432 lines from AMDGPU's generated NBIO 7.0 shift/mask header. It contains 2,147 `#define` field-layout constants and 279 register-family comments. There are no functions, structs, enums, variables, executable statements, locks, allocations, or direct MMIO/SMN/PCI configuration accesses in this range.

The range starts in the middle of `BIF_CFG_DEV0_RC2_PCIE_LANE_7_EQUALIZATION_CNTL`, after the shift definitions and at the remaining masks for lane 7. It then covers lane 8 through lane 15 equalization and ACS definitions for `DEV0_RC2`, the complete `addressBlock: nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp`, and most of `addressBlock: nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`. It ends inside `BIF_CFG_DEV0_EPF0_3_PCIE_ACS_CNTL` after the `SOURCE_VALIDATION_EN_MASK`; the remaining ACS control masks continue in the next chunk.

Although this file is under a `ceph-client` source mirror, the content is AMD GPU/NBIO PCIe register metadata and has no distributed-filesystem or Ceph behavior.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of the generated NBIO 7.0 register interface. Each exported macro gives either:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position of a hardware field.
- `<REGISTER>__<FIELD>_MASK`, the register mask used to isolate or update that field.

This chunk focuses on NBIF0 PCI configuration-space decode blocks. `BIF_CFG_DEV1_RC2_*` describes a PCIe root-complex/bridge-style function with standard PCI header fields, PCI PM, PCIe, MSI, SSID, MSI-map, vendor-specific, virtual-channel, device-serial-number, AER, secondary PCIe, lane equalization, and ACS capability fields. `BIF_CFG_DEV0_EPF0_3_*` describes an endpoint-function configuration-space block with standard endpoint header fields, BARs, ROM BAR, vendor and adapter IDs, PCI PM, PCIe, MSI/MSI-X, VC, serial number, AER, BAR enhanced capability, power-budget, dynamic power allocation, secondary PCIe, lane equalization, and ACS fields.

The header does not configure PCIe, expose a runtime API, or enforce sequencing. It supplies symbolic field geometry to code that performs those operations through companion offset/default headers and AMDGPU register helpers.

## Important Macro Families

The opening partial section completes `BIF_CFG_DEV0_RC2` lane-equalization and ACS field masks:

- `BIF_CFG_DEV0_RC2_PCIE_LANE_7_EQUALIZATION_CNTL` ends with the downstream/upstream TX preset and RX preset-hint masks plus the reserved bit mask.
- `BIF_CFG_DEV0_RC2_PCIE_LANE_8_EQUALIZATION_CNTL` through lane 15 repeat the same layout: downstream TX preset at bits 0-3, downstream RX preset hint at bits 4-6, upstream TX preset at bits 8-11, upstream RX preset hint at bits 12-14, and a reserved bit at bit 15.
- `BIF_CFG_DEV0_RC2_PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, and `PCIE_ACS_CNTL` define Access Control Services capability IDs, version/next pointers, support bits, and enable bits for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, P2P egress control, and direct translated P2P.

The `BIF_CFG_DEV1_RC2_*` block is a complete bridge/root-port-style PCI config-space map:

- Standard PCI identity and bridge header fields: vendor/device ID, command/status, revision/class code, cache line, latency, header type, BIST, bridge BAR, bus numbers, I/O base/limit, memory base/limit, prefetchable base/limit upper/lower fields, capability pointer, interrupt line/pin, bridge control, and extended bridge control.
- Power-management capability: PM capability list/header fields, supported D-states, PME support, version, next pointer, and PM status/control fields such as power state, PME enable/status, data select, data scale, and bus-power/clock-control bits.
- PCIe capability: PCIe capability header, device/link/slot/root capability, control, and status registers; capability 2, device control/status 2, link capability/control/status 2, and slot control/status 2.
- MSI and MSI mapping: MSI capability list, message control, 32-bit/64-bit message address/data, MSI map capability, and MSI map base address fields.
- Subsystem ID and vendor-specific enhanced capability scratch/header fields.
- Virtual Channel capability: port VC capability/control/status plus VC0 and VC1 resource capability/control/status, TC-to-VC maps, arbitration tables, VC IDs, and enable/status bits.
- Device serial number enhanced capability: low and high 32-bit serial number fields.
- Advanced Error Reporting: uncorrectable/correctable error status, masks, severity, AER capability/control, header logs, root error command/status, error source IDs, and TLP prefix logs.
- Secondary PCIe and ACS: link control 3, lane error status, per-lane equalization control registers for lanes 0-15, ACS enhanced capability list, ACS capability, and ACS control.

The `BIF_CFG_DEV0_EPF0_3_*` block is an endpoint-function PCI config-space map:

- Standard endpoint header fields: vendor/device ID, command/status, revision/class, cache line, latency, header type, BIST, BAR1 through BAR6, adapter ID, ROM base address, capability pointer, interrupt line/pin, min grant, and max latency.
- Vendor/adapter and power-management capabilities: vendor capability list, adapter ID write field, PM capability, and PM status/control.
- PCIe endpoint capability: device/link capability, control, and status registers; capability 2, device/link control/status 2, and slot-control/status 2 definitions present in this endpoint block.
- MSI/MSI-X: MSI message control, address/data, mask and pending fields including 64-bit variants; MSI-X capability list, message control, table, and PBA fields.
- Vendor-specific, VC, serial-number, and AER enhanced capabilities: same broad capability families as `DEV1_RC2`, with endpoint-specific root-error fields absent where not applicable in this range.
- BAR enhanced capability: BAR1 through BAR6 capability/control fields for BAR sizing/indicator/prefetchability and control enablement.
- Power budget and DPA: power-budget data select/data/capability fields, DPA capability, latency indicator, status, control, and substate power allocations 0-7.
- Secondary PCIe and lane equalization: link control 3, lane error status, lane 0-15 equalization control layouts, and the beginning of ACS capability/control.

## APIs, Types, And Functions

There are no callable APIs, C types, or local helper functions in this chunk. The exported interface is the generated macro namespace. The constants are untyped C preprocessor integer literals, typically suffixed with `L`, and must be paired with:

- `nbio_7_0_offset.h` for register offsets/address selectors.
- `nbio_7_0_default.h` for reset/default values.
- AMDGPU register helpers such as field extraction/composition helpers and MMIO, SMN, or PCI configuration accessors selected by the consuming code.

The macros encode only field location and width. They do not encode read/write permissions, reset value, access size, write-one-to-clear behavior, self-clearing behavior, firmware ownership, side effects, or required ordering.

## Control Flow

This header has no local runtime control flow. Runtime usage is external and typically follows this pattern:

1. Driver code selects an NBIO 7.0 register offset from the generated offset header.
2. It reads a PCIe/NBIO register through the appropriate AMDGPU access path.
3. It decodes a field with a `__SHIFT` and `_MASK`, or composes a read-modify-write value while preserving unrelated bits.
4. Hardware reacts according to PCIe/NBIO semantics: configuration-space enablement, link control, interrupt programming, AER status/mask changes, ACS routing/isolation policy, power-management policy, BAR/DPA capability handling, or lane equalization state.

The source order follows the generated register database, not an execution sequence. Several logical hardware flows are represented by field names: PCI enumeration and bridge-window programming, endpoint BAR/resource programming, MSI/MSI-X setup, PCI PM and PCIe power-management negotiation, AER error reporting, virtual-channel arbitration, secondary PCIe lane equalization, ACS policy, power budgeting, DPA substate selection, and link diagnostics.

## State And Persistence Behavior

The header owns no software state and persists nothing. It names hardware-visible fields in NBIO PCI configuration-space decode blocks. Persistence depends on PCI reset semantics, GPU/NBIO reset domains, function-level reset, power state transitions, firmware/BIOS initialization, suspend/resume restore, and explicit driver writes.

The represented hardware state includes:

- Configuration controls such as command bits, bus mastering, memory/I/O decode, interrupt disable, bridge controls, link controls, MSI/MSI-X enables, AER masks, ACS enables, VC resource controls, BAR controls, PM/DPA controls, and power-budget selectors.
- Capability and identity fields such as vendor/device ID, class code, capability IDs, link capability, slot/root/device capabilities, serial number, BAR capability descriptors, DPA capability, and ACS support bits.
- Status or sticky fields such as PCI status, secondary status, device/link/slot/root status, AER error status, lane error status, MSI pending bits, DPA status, VC status, and power-management status.
- Command-like fields such as secondary bus reset, link retrain, PME status/enable, AER root error commands, VC arbitration load/select, BAR control updates, DPA transition controls, and MSI/MSI-X mask bits.

The shift/mask definitions cannot be used alone to decide whether a field is volatile, sticky, write-one-to-clear, read-only, write-only, reserved, or self-clearing. Consumers must rely on PCIe specifications, AMD hardware documentation, and local driver policy.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 7.0 register-header set staying synchronized:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_offset.h` supplies the matching register addresses.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h` supplies matching default values; the `BIF_CFG_DEV1_RC2_*` and `BIF_CFG_DEV0_EPF0_3_*` names appear there as `smn..._DEFAULT` definitions.
- AMDGPU SOC15/NBIO platform code includes the NBIO 7.0 generated headers to access ASIC-specific registers.

The practical integration points are PCIe and NBIF behavior rather than file-system logic: GPU enumeration, bridge/root-complex configuration, endpoint-function resource setup, interrupt setup, AER handling, ACS/IOMMU isolation policy, PCIe link training and diagnostics, ASPM/power management, MSI/MSI-X table handling, virtual-channel programming, BAR capability reporting, power-budget/DPA reporting, reset/recovery, and debug register dumps.

## Risks And Edge Cases

- The chunk starts and ends mid-register-family. `DEV0_RC2` lane 7 shifts are before this chunk, and the remaining `DEV0_EPF0_3_PCIE_ACS_CNTL` masks are after this chunk. File-level conclusions must reconcile adjacent chunks.
- A wrong generated shift or mask can compile cleanly while writing the wrong PCIe configuration bit, clearing adjacent status, misreporting capability support, or breaking interrupt, link, or isolation behavior.
- PCI status, secondary status, device status, root status, AER status, MSI pending, and similar fields may be sticky or write-one-to-clear. Generic read-modify-write code can accidentally clear errors if it writes status registers without W1C-aware handling.
- `COMMAND`, BAR, ROM BAR, bridge resource-window, bus-number, and bridge-control masks can affect whether devices decode memory/I/O, whether bus mastering is allowed, and whether downstream resources are reachable.
- `SECONDARY_BUS_RESET`, link retrain/disable, target speed, compliance, DPA, and power-management control fields can disrupt active devices or links if written outside controlled reset or power-management sequences.
- MSI and MSI-X fields distinguish message address/data, enable/mask, table/PBA location, and pending bits. Confusing pending/status fields with masks or enables can cause lost or stuck interrupts.
- AER status, mask, and severity registers often use identical bit positions with different meanings. Copying fields between status/mask/severity contexts can change whether errors are reported, suppressed, classified fatal, or cleared.
- ACS fields affect peer-to-peer routing and isolation. Incorrect capability/control decoding can affect IOMMU grouping, VFIO/passthrough assumptions, SR-IOV-style isolation, or peer DMA policy.
- Lane equalization control is repeated for lanes 0-15. Off-by-one lane selection or a prefix mix-up between `DEV0_RC2`, `DEV1_RC2`, and `DEV0_EPF0_3` can appear only as link training instability on certain widths or speeds.
- The endpoint `EPF0_3` block includes MSI-X, BAR enhanced capability, power-budget, and DPA fields that have different semantics from the bridge/root-port `DEV1_RC2` block. Similar field names should not be treated as interchangeable across function types.
- Reserved masks are present throughout. Writers must preserve reserved bits unless authoritative hardware documentation explicitly permits writing them.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.0/SOC15 support. Compile failures catch malformed generated symbols or missing companion definitions.
- Run generated-header consistency checks against the authoritative NBIO 7.0 register database: every field should have the expected shift/mask, every register should have a matching offset entry, and default values should exist where defined.
- Cross-check repeated lane equalization families for lanes 0-15 across `DEV0_RC2`, `DEV1_RC2`, and `DEV0_EPF0_3`: the field layouts should match except for the register prefix.
- Validate PCIe enumeration on supported hardware: vendor/device/class IDs, bridge bus numbers, I/O and memory windows, BARs, ROM BAR, command/status, capability pointers, and PCIe capability chains should decode coherently with `lspci -vv` or equivalent diagnostics.
- Exercise MSI/MSI-X setup, vector masking/unmasking, pending-bit visibility, suspend/resume restore, GPU reset restore, and interrupt delivery under load for functions using these NBIF config-space blocks.
- Exercise PCIe link behavior: negotiated speed/width, link retraining, lane error reporting, Gen speed changes, equalization status, ASPM/PM transitions, and reset recovery.
- Exercise AER handling where available: correctable and uncorrectable status, mask, severity, header-log, TLP-prefix-log, root-error command/status, and error-source-ID decoding.
- Validate ACS and IOMMU grouping/passthrough behavior on platforms exposing these blocks, especially when peer-to-peer DMA or virtualization depends on isolation.
- Validate power-related reporting and controls for endpoint functions: PCI PM status/control, power-budget data selection, DPA status/control, and DPA substate power allocation values across cold boot, warm reset, and resume.
- Include boundary checks during merge: complete `BIF_CFG_DEV0_RC2_PCIE_LANE_7_EQUALIZATION_CNTL` from the prior chunk and complete `BIF_CFG_DEV0_EPF0_3_PCIE_ACS_CNTL` from the following chunk before producing the final per-file report.

### subset-b-003111: lines 104919-107381

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 104919-107381

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 2,077 `#define` field-layout macros and no functions, structs, enums, variables, allocations, locks, or executable statements.

The range starts at the tail of `BIF_CFG_DEV0_EPF0_3_PCIE_ACS_CNTL`, continues through the remaining EPF0 PCIe enhanced capability and GPU IOV field definitions, covers most of the `addressBlock: nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` register field definitions, and ends just after `BIF_CFG_DEV0_EPF2_2_MIN_GRANT` begins in the next `addressBlock: nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` section. Adjacent chunks are required for complete EPF0 ACS context before this range and complete EPF2 config-space context after it.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield companion to AMDGPU's generated NBIO 7.0 register address/default headers. For every register field in this slice it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position for encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate, clear, preserve, or update the field.

This slice models PCIe endpoint-function configuration space and extended capabilities for NBIF device 0 functions, especially EPF0 and EPF1 plus the beginning of EPF2. It gives driver code symbolic field positions for PCIe identity/configuration registers, power management, PCIe link/device capabilities, MSI/MSI-X, virtual channels, AER, BAR sizing/control, dynamic power allocation, secondary PCIe equalization, ACS/ATS/PRI/PASID/TPH/multicast/LTR/ARI/SR-IOV, and AMD vendor-specific GPU IOV controls.

## Important Macro Families

The opening EPF0 tail covers PCIe security, translation, virtualization, and GPU IOV fields. It includes ACS control bits for source validation, translation blocking, peer-to-peer redirection, upstream forwarding, egress control, and direct translated peer-to-peer operation. It then defines ATS capability/control fields, PRI page-request control/status/capacity/allocation, PASID capability/control, TPH requester capability/control, multicast group/window controls, LTR latency capability, ARI capability/control, and SR-IOV capability/control/status/VF BAR/page-size/function-link fields.

The EPF0 GPU IOV VSEC section defines the vendor-specific enhanced capability list/header, SR-IOV shadow state, interrupt enable/status bits for GFX/UVD/VCE command completion, hang recovery, FLR-needed, VM-busy transitions, and HVVM mailbox events. It also defines `SOFT_PF_FLR`, HVVM mailbox dwords with VF index, transmit/receive message data, valid/ack bits, per-VF `TRN_ACK`/`RCV_VALID` bits for VF0 through VF15, PF mailbox status bits, context/current-VF fields, total frame-buffer size, VF frame-buffer offset/size pairs for VF0 through VF15, and full-dword scheduler payload registers for UVD, VCE, and GFX.

The EPF1 address block starts with standard PCI configuration-space fields: vendor/device ID, command bits, status bits, revision/class/subclass/prog-if, cache line, latency, header/BIST, BAR1 through BAR6, subsystem adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. It then defines vendor capability and power-management capability/status/control fields.

The EPF1 PCIe capability section covers device and link registers: max payload and read request sizes, relaxed ordering, no-snoop, FLR initiation, error enables/status, link speed/width, ASPM and clock power management, retrain/link-disable controls, link status, Device Capabilities 2, Device Control 2, Link Capabilities/Control/Status 2, and the PCIe slot capability/control/status 2 placeholders.

The EPF1 interrupt and extended capability groups include MSI and MSI-X control/table/PBA fields, generic vendor-specific scratch registers, virtual-channel capabilities and VC0/VC1 resource controls, device serial number dwords, and Advanced Error Reporting status/mask/severity/capability/header-log/TLP-prefix-log fields. AER fields cover DLP, surprise down, poisoned TLP/sequence number, flow control, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, TLP prefix blocked, receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal error, correctable internal error, header-log overflow, ECRC generation/check enables, and multiple-header-record controls.

The later EPF1 capability groups define BAR enhanced capabilities for BAR1 through BAR6, power budget data selection/data/capability, DPA capability/status/control and eight substate power-allocation fields, secondary PCIe link-control/lane-error/equalization fields for lanes 0 through 15, ACS, ATS, PRI, PASID, TPH, multicast, LTR, ARI, SR-IOV, and the same GPU IOV VSEC/mailbox/frame-buffer/scheduler families seen for EPF0. The chunk ends after EPF2 standard identity/config/header/BAR/subsystem/ROM/capability-pointer/interrupt fields and the `MIN_GRANT` comment.

## APIs, Types, And Functions

There are no callable APIs or C types in this range. The public interface is the generated preprocessor macro namespace. All constants are integer literals, usually with an `L` suffix, intended for C bit manipulation.

Consumers combine these field definitions with companion register address/default headers and AMDGPU access helpers such as SOC15, PCIe config, MMIO, SMN, or indirect register read/write helpers. A typical consumer reads a register, extracts a field with `mask` and `shift`, or does a read/modify/write that clears the mask and inserts `(value << shift) & mask`.

These macros do not encode register addresses, access widths, access permissions, write-one-to-clear behavior, reset values, reserved-bit rules, firmware ownership, synchronization requirements, or required delays. Those properties must come from the hardware register database, sibling generated headers, and call-site-specific driver logic.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU, platform firmware, PCI core, or virtualization code selects a NBIO/PCIe configuration register address from the matching offset/SMN metadata.
2. The caller reads or composes a register value through the relevant access path.
3. The shift/mask constants in this chunk identify the field within the register value.
4. Hardware state machines then apply the change or report status for PCIe link/device control, AER, MSI/MSI-X, virtual-channel negotiation, ACS/ATS/PRI/PASID translation services, SR-IOV VF enumeration, GPU IOV mailbox exchange, or FLR/reset handling.

Several represented flows are asynchronous and require polling, interrupts, or sequencing outside this file: link retraining, FLR initiation, AER status clearing, MSI/MSI-X table setup, VC arbitration table loads and negotiation, DPA substate transitions, lane equalization phases, PRI/ATS/PASID enablement, SR-IOV VF enablement, GPU IOV mailbox valid/ack handshakes, and per-engine virtualization/hang-recovery interrupts.

## State And Persistence Behavior

The header owns no mutable software state and persists nothing. It describes hardware-visible state stored in PCIe configuration space and NBIO vendor-specific extended capability registers.

Represented state includes read-only identity/capability fields, writable command/control bits, sticky or latched status bits, BAR and ROM apertures, interrupt routing state, MSI/MSI-X masks and pending bits, link speed/width/training state, AER masks/severity/header logs, virtual-channel resource state, ACS/ATS/PRI/PASID/TPH controls, SR-IOV VF counts and BARs, and AMD GPU IOV mailbox/frame-buffer/scheduler state. Some fields are standard PCIe capability state exposed to the Linux PCI subsystem; others are AMD-specific PF/VF virtualization controls.

Persistence depends on the reset domain and access type: PCI conventional reset, FLR, hot reset, GPU reset, NBIO reset, platform firmware initialization, suspend/resume restore, SR-IOV enable/disable, and hypervisor or PF driver ownership. The shift/mask file does not indicate which fields are sticky, which are write-one-to-clear, which are read-only mirrors, or which are lost across PF/VF reset.

## Dependencies And Integration Points

This generated chunk must stay synchronized with `nbio_7_0_offset.h`, `nbio_7_0_default.h`, `nbio_7_0_smn.h`, and AMD's source register database. The register names in this file are useful only when paired with matching register offsets and default/access metadata.

Driver integration points include AMDGPU NBIO initialization, PCIe capability discovery, PCI command and BAR setup, MSI/MSI-X routing, AER policy, PCIe link management, runtime power management, FLR/GPU reset flows, SR-IOV PF/VF enablement, VF BAR sizing, GPU IOV frame-buffer partitioning, mailbox-based PF/VF communication, engine scheduling for GFX/UVD/VCE, ATS/PRI/PASID interactions with IOMMU support, ACS isolation, and debug/diagnostic register dumps.

The PCIe-standard fields intersect with the Linux PCI core and generic PCIe services. The AMD-specific GPU IOV VSEC fields are tighter integration points for virtualization stacks because they carry per-VF mailbox acknowledgements, per-VF frame-buffer partitions, and per-engine scheduler dwords. Incorrect ownership assumptions between PF, VF, firmware, and hypervisor code can break isolation or reset recovery.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while targeting the wrong bit, which can corrupt PCIe config-space programming, link state, interrupts, AER masks, SR-IOV layout, or GPU IOV mailbox semantics.
- This chunk begins and ends on logical boundaries split across neighboring chunks. EPF0 ACS control starts before line 104919, and EPF2 `MIN_GRANT` continues after line 107381.
- Several register families reuse similar field names across EPF0, EPF1, and EPF2. Accidentally mixing `EPF0_3`, `EPF1_2`, and `EPF2_2` constants can silently operate on the wrong endpoint-function layout.
- Status, mask, severity, and control registers have nearly identical AER field names. Using a status mask against a mask/severity/control register, or clearing a W1C status field with ordinary read/modify/write assumptions, can lose diagnostics or fail to unmask real faults.
- PCIe link and equalization fields are timing-sensitive. Retrain, link-disable, target speed, lane equalization, ASPM, and clock power-management writes need platform-aware sequencing and timeouts.
- SR-IOV fields affect VF count, function dependency, first VF offset, VF stride, VF device ID, VF BARs, and migration array placement. Bad programming can break VF enumeration or expose resources incorrectly.
- GPU IOV frame-buffer fields split each VF's offset and size. Unit mismatches, overflows, overlap, or stale values after reset can violate VF isolation.
- HVVM mailbox fields require valid/ack handshakes across PF and VF contexts. Reusing stale `VF_INDEX`, failing to clear valid bits, or racing per-VF ack/receive-valid bits can lose messages or attribute them to the wrong VF.
- Full-width `0xFFFFFFFFL` masks appear for BARs, serial-number dwords, message addresses, scratch registers, scheduler dwords, and frame-buffer related payloads. Full-width field masks do not imply that arbitrary writes are safe.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time coverage catches missing or renamed generated symbols referenced by consumers.
- Run generated-header consistency checks for this slice: every field should have matching `__SHIFT` and `_MASK` macros, masks should match their declared shift/width, and repeated VF/lane/BAR/scheduler patterns should be monotonic and complete.
- Cross-check each register family in this chunk against `nbio_7_0_offset.h` and `nbio_7_0_default.h` so field definitions map to known register addresses and reset/default values.
- On NBIO 7.0 hardware, validate PCI enumeration, BAR sizing, MSI/MSI-X setup, AER reporting/clearing, link speed/width reporting, link retrain, suspend/resume, FLR, GPU reset, and runtime power transitions.
- For SR-IOV capable configurations, enable/disable VFs, verify VF counts/strides/device IDs/BARs, test PF and VF FLR, and confirm VF resource isolation across reset and resume.
- For GPU IOV paths, exercise PF/VF mailbox transmit/receive/ack transitions, per-engine command-complete and hang/FLR-needed interrupts, frame-buffer partition programming for VF0 through VF15, and scheduler dword programming for GFX/UVD/VCE.
- Validate ACS/ATS/PRI/PASID interactions with the IOMMU and PCI core: translation enablement, page-request status/error handling, PASID width/permission bits, and peer-to-peer isolation policy.

### subset-b-003112: lines 107382-109840

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 107382-109840

## Scope

This chunk is part of the generated AMD NBIO 7.0 register shift/mask header used by the amdgpu driver. It covers PCI/PCIe configuration-space bitfield definitions for `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, all of `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`, and the beginning of `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`. The range starts just after `BIF_CFG_DEV0_EPF2_2_MIN_GRANT` and ends at the comment for `BIF_CFG_DEV0_EPF4_2_PCIE_BAR4_CNTL`, so EPF4 is intentionally partial in this chunk.

The file is not executable logic. It exposes `#define` constants of the form:

- `REGISTER__FIELD__SHIFT`, the bit position for a field.
- `REGISTER__FIELD_MASK`, the mask for that field in the register value.

These constants are consumed by register helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `WREG32_SOC15`, `RREG32_SOC15`, and `WREG32_FIELD15` in amdgpu code after including the companion `nbio_7_0_offset.h`, `nbio_7_0_default.h`, and `nbio_7_0_smn.h` headers.

## Purpose

The chunk describes the NBIO 7.0 PCIe endpoint-function configuration register layout for virtual or exposed functions `DEV0_EPF2`, `DEV0_EPF3`, and part of `DEV0_EPF4`. The layout mirrors PCI conventional configuration space and PCIe extended capabilities:

- Base PCI identity, command, status, BAR, ROM, interrupt, and class-code fields.
- PCI Power Management Interface registers.
- PCIe capability registers for device, link, slot, and Gen2/Gen3-style extensions.
- MSI and MSI-X capability registers.
- SATA capability placeholders exposed through this NBIO config decode block.
- PCIe vendor-specific, AER, BAR enhanced allocation, power budget, dynamic power allocation, access control services, and alternative routing ID interpretation capability registers.

The definitions let driver code read, update, or decode hardware state without hard-coding bit positions. The masks also act as a local hardware contract: if a field moves in a future ASIC revision, callers must use the revision-specific header rather than reusing this one.

## Important Definitions

The chunk is organized by repeated endpoint-function prefixes:

- `BIF_CFG_DEV0_EPF2_2_*`: completes EPF2 from `MAX_LATENCY` through `PCIE_ARI_CNTL`.
- `BIF_CFG_DEV0_EPF3_2_*`: full EPF3 config block from `VENDOR_ID` through `PCIE_ARI_CNTL`.
- `BIF_CFG_DEV0_EPF4_2_*`: partial EPF4 config block from `VENDOR_ID` through the beginning of BAR enhanced allocation (`PCIE_BAR4_CNTL` comment at the range end).

Key register groups in each complete EPF block:

- PCI command/status: `COMMAND` includes I/O, memory, bus master, special cycle, memory-write-invalidate, VGA palette snoop, parity/error-response, SERR, fast back-to-back, interrupt disable, and atomic-operation requester controls. `STATUS` covers interrupt status, capability-list presence, frequency, fast-back-to-back, parity, devsel timing, target/master aborts, signaled system error, parity error, and atomic-op egress-blocked status.
- Identification and BAR layout: `VENDOR_ID`, `DEVICE_ID`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `HEADER`, `BIST`, `BASE_ADDR_1` through `BASE_ADDR_6`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, `INTERRUPT_LINE`, and `INTERRUPT_PIN`.
- Power management: `PMI_CAP_LIST`, `PMI_CAP`, and `PMI_STATUS_CNTL` expose capability chaining, PME support, power state, PME enable/status, data select/scale, bus-power enable, and PMI data fields.
- PCIe core capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, and `LINK_STATUS`.
- PCIe second-generation capability: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2`.
- Interrupt capability: `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, 64-bit MSI variants, pending bits, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- PCIe AER: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0..3`, and `PCIE_TLP_PREFIX_LOG0..3`.
- Resource and power extended capabilities: `PCIE_BAR_ENH_CAP_LIST`, `PCIE_BAR{1..6}_CAP`, `PCIE_BAR{1..6}_CNTL`, `PCIE_PWR_BUDGET_ENH_CAP_LIST`, `PCIE_PWR_BUDGET_DATA_SELECT`, `PCIE_PWR_BUDGET_DATA`, `PCIE_PWR_BUDGET_CAP`, `PCIE_DPA_ENH_CAP_LIST`, `PCIE_DPA_CAP`, `PCIE_DPA_LATENCY_INDICATOR`, `PCIE_DPA_STATUS`, `PCIE_DPA_CNTL`, and `PCIE_DPA_SUBSTATE_PWR_ALLOC_0..7`.
- Isolation and routing: `PCIE_ACS_ENH_CAP_LIST`, `PCIE_ACS_CAP`, `PCIE_ACS_CNTL`, `PCIE_ARI_ENH_CAP_LIST`, `PCIE_ARI_CAP`, and `PCIE_ARI_CNTL`.

The AER uncorrectable status/mask/severity groups are among the densest groups in the range. They include data-link protocol, surprise-down, poisoned TLP, flow-control protocol, completion timeout, completer abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, MC blocked TLP, atomic-op egress blocked, and TLP prefix blocked bits.

## Control Flow

There is no run-time control flow inside this header. Control flow exists only in code that includes it. For NBIO 7.0, direct users include `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`. Those files combine this mask header with the NBIO offset/default/SMN headers and the amdgpu register access wrappers.

The typical call pattern is:

1. Select an NBIO register offset from `nbio_7_0_offset.h` or an SMN address from `nbio_7_0_smn.h`.
2. Read a 32-bit register with an amdgpu helper.
3. Extract or modify a field using this header's `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` constants, often through `REG_GET_FIELD` or `REG_SET_FIELD`.
4. Write the updated register value back when the field is writable.

Within this chunk, the PCIe endpoint configuration fields are more likely to be decoded, exposed, or preserved than frequently written by generic driver code. Some writable classes are still important: command enables, power-management state, link controls, MSI/MSI-X enables and masks, AER masks/severity controls, BAR enhanced allocation controls, ACS controls, ARI controls, and DPA controls.

## State and Persistence

The header itself has no state and persists nothing. The state represented by these masks lives in NBIO hardware registers and PCIe configuration-space shadows. Values are hardware/firmware initialized at boot and can be changed by firmware, PCI core enumeration, amdgpu initialization, runtime power management, error handling, virtualization setup, or reset paths.

The companion default header shows the intended reset/default values for the same register names. In the complete EPF2 and EPF3 blocks, defaults include enabled PCIe capability-list pointers, FLR-capable device capability (`DEVICE_CAP` default `0x10000000`), link capability/status defaults, MSI capability defaults, AER severity/mask defaults, BAR enhanced allocation list defaults, power budget capability chaining, DPA status defaults, and ACS/ARI extended-capability defaults. This mask header should therefore be treated as the field map for persistent hardware state across reset domains, not as a configuration policy source.

## Dependencies and Integration Points

Primary dependencies:

- `nbio_7_0_offset.h` supplies MMIO register offsets for NBIO 7.0 registers.
- `nbio_7_0_smn.h` supplies SMN addresses for indirect or fabric-visible NBIO registers.
- `nbio_7_0_default.h` supplies expected hardware defaults for the same register names.
- amdgpu register helpers in the driver use the shift/mask naming convention directly.

Integration points:

- `amdgpu/nbio_v7_0.c` includes this header for NBIO 7.0 operations such as memory-controller access enable, revision-id extraction, doorbell range setup, interrupt control, HDP flush/remap offsets, and clock-gating/light-sleep control. That file demonstrates the broader usage pattern even though it does not directly manipulate every endpoint-function PCIe field in this chunk.
- `amdgpu/soc15.c` includes this header as part of SOC15 device setup, where ASIC family routing determines which IP blocks and register maps are active.
- `pm/powerplay/hwmgr/smu10_inc.h` includes this NBIO map alongside MP and THM register maps for SMU10-era power-management code.
- The kernel PCI core and platform firmware define the semantic meaning of many fields here; this header provides AMD-specific bit locations within the NBIO register decode.

## Risks

- Register-family mismatch is the primary risk. These masks are only valid for NBIO 7.0. Reusing them with NBIO 7.2, 7.4, 7.9, or later hardware can silently read or write the wrong bits.
- The range contains repeated, near-identical EPF2/EPF3/EPF4 definitions. Manual edits or generated-header drift can introduce copy/paste skew where one endpoint function no longer matches the others.
- The slice ends mid-EPF4 BAR enhanced-allocation section. Any consumer research that treats this chunk as the full EPF4 block would miss later EPF4 BAR5/BAR6, power budget, DPA, ACS, and ARI fields outside the requested line range.
- Write masks for PCI command, link control, MSI/MSI-X, AER, ACS, ARI, and DPA fields are sensitive. Incorrect use can disable memory or bus-master access, break interrupt delivery, alter error reporting, weaken isolation, or create link/power-management instability.
- Some AER status fields are write-one-to-clear in PCIe-style designs. Code using these masks must respect hardware semantics and avoid read-modify-write patterns that accidentally clear latched errors.
- BAR enhanced allocation and ACS/ARI fields affect resource routing and function isolation. Misprogramming can cause peer-to-peer access or VF/function routing behavior that conflicts with IOMMU and PCI core expectations.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-observation based:

- Kernel build coverage for amdgpu with NBIO 7.0/SOC15 support ensures all macro names used by driver code still resolve.
- Static comparison against generated register specifications or adjacent NBIO revision headers can catch prefix or mask drift across repeated EPF blocks.
- Runtime PCI enumeration should still show coherent capability lists for the affected functions: PM, PCIe, MSI/MSI-X, AER, enhanced allocation, power budget, DPA, ACS, and ARI where enabled by defaults.
- `lspci -vvv` on matching hardware can verify link capability/status, MSI/MSI-X capability, AER fields, ACS/ARI presence, BAR sizing, and power-management capability state.
- AER testing should confirm correct reporting and clearing of correctable/uncorrectable errors without spurious status loss.
- Reset and suspend/resume testing should confirm that command enables, interrupt state, link state, BAR-related fields, and power-management fields return to expected defaults or driver-restored values.
- SR-IOV or multi-function tests, when applicable to the endpoint functions represented by EPF2/EPF3/EPF4, should confirm function isolation, ARI routing, ACS behavior, and interrupt delivery remain consistent.

### subset-b-003113: lines 109841-112318

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

### subset-b-003114: lines 112319-114771

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 112319-114771

## Scope

This chunk is a generated AMD NBIO 7.0 register bitfield mask header segment. It contains `#define` constants for field shifts and field masks, not executable code. The covered range begins in the tail of the `BIF_CFG_DEV0_EPF7_2` PCI configuration-space decode block, covers the complete `BIF_CFG_DEV1_EPF0_2` block, and starts the `BIF_CFG_DEV1_EPF1_2` block through the first DPA capability fields. The definitions are consumed by code that includes `nbio_7_0_sh_mask.h` together with the paired NBIO offset/default headers.

## Purpose

The purpose of this chunk is to provide stable symbolic field layouts for AMD NBIO/BIF PCIe configuration registers. Each register receives one or more `REGISTER__FIELD__SHIFT` and `REGISTER__FIELD_MASK` macros, allowing driver code to extract or compose individual fields without embedding raw bit arithmetic at call sites.

The chunk models PCI configuration and extended capability structures for endpoint/function slices:

- `BIF_CFG_DEV0_EPF7_2`: SATA capability, vendor-specific capability, Advanced Error Reporting, BAR capability/control, power budget, Dynamic Power Allocation, Access Control Services, and ARI capability fields.
- `BIF_CFG_DEV1_EPF0_2`: full PCI config header fields plus power management, PCIe capability, MSI/MSI-X, SATA, vendor-specific, Virtual Channel, Advanced Error Reporting, BAR, power budget, DPA, Secondary PCIe extended capability, per-lane equalization, ACS, LTR, and ARI fields.
- `BIF_CFG_DEV1_EPF1_2`: full PCI config header prefix through MSI/MSI-X, SATA/vendor-specific, AER, BAR, power budget, and DPA capability fields up to `PWR_ALLOC_SCALE`.

## Important APIs, Types, and Macros

There are no C types or functions in this chunk. The important public interface is the generated macro naming convention:

- `REGISTER__FIELD__SHIFT` gives the field's least-significant bit position.
- `REGISTER__FIELD_MASK` gives the field mask in the register's native width, usually 16 or 32 bits.
- AMDGPU's helper macros in `drivers/gpu/drm/amd/amdgpu/amdgpu.h` compose these names:
  - `REG_FIELD_SHIFT(reg, field)` expands to `reg##__##field##__SHIFT`.
  - `REG_FIELD_MASK(reg, field)` expands to `reg##__##field##_MASK`.
  - `REG_SET_FIELD(orig_val, reg, field, field_val)` clears the mask and inserts a shifted field value.
  - `REG_GET_FIELD(value, reg, field)` masks and shifts a raw register value.

Important register groups in the chunk:

- PCI identity/header: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1..6`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt line/pin, and latency grant fields for `DEV1_EPF0` and `DEV1_EPF1`.
- PCIe capability: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X: message control, address/data, masks, pending bits, table BAR indicator, and PBA offsets.
- Advanced Error Reporting: uncorrectable/correctable status, mask, severity, `ADV_ERR_CAP_CNTL`, four TLP header log registers, and four TLP prefix log registers.
- BAR enhanced capability: capability header plus `BAR1..BAR6` supported-size and control fields.
- Power management extensions: Power Budgeting capability/data and DPA capability/status/control/substate allocation fields.
- PCIe isolation/routing extensions: ACS capability/control, ARI capability/control, LTR for `DEV1_EPF0`, and VC capability/resource fields for `DEV1_EPF0`.
- Link training diagnostics for `DEV1_EPF0`: secondary capability, `LINK_CNTL3`, `LANE_ERROR_STATUS`, and lane 0 through lane 15 equalization controls.

## Control Flow

This header has no runtime control flow. Its effective control flow is compile-time token expansion:

1. A driver source includes `nbio_7_0_sh_mask.h` alongside the matching NBIO register address/default headers.
2. The source reads or prepares a raw register value through AMDGPU register accessors.
3. `REG_GET_FIELD()` or `REG_SET_FIELD()` expands the selected `REGISTER__FIELD` pair into a mask/shift operation.
4. The resulting value is used for initialization, feature detection, error reporting, interrupt configuration, power management, or PCIe link handling.

Because this chunk covers PCI config-space-like structures, runtime accesses are normally mediated by NBIO/BIF register addressing and platform-specific register access layers rather than by this file directly.

## State and Persistence Behavior

The macros do not store state and do not persist values. The state they describe lives in hardware registers:

- Status fields, such as AER correctable and uncorrectable status bits, reflect PCIe error state latched by hardware and often require write-to-clear behavior at the register access layer.
- Control fields, such as MSI/MSI-X enable bits, PCIe Device Control flags, BAR sizing controls, DPA controls, ACS controls, and ARI controls, persist in the device's register/configuration state until reset or reprogramming.
- Capability fields, such as BAR sizes, ECRC support, link speeds, power allocation scales, and ARI/ACS support, are hardware capability descriptors and should usually be treated as read-only by higher-level code.
- Default reset values are described in `nbio_7_0_default.h`, not in this `sh_mask` chunk. For example, defaults exist for covered symbols such as `smnBIF_CFG_DEV0_EPF7_2_SATA_CAP_0_DEFAULT`, `smnBIF_CFG_DEV1_EPF0_2_VENDOR_ID_DEFAULT`, `smnBIF_CFG_DEV1_EPF1_2_VENDOR_ID_DEFAULT`, and `smnBIF_CFG_DEV1_EPF1_2_PCIE_DPA_CAP_DEFAULT`.

## Dependencies

The chunk depends on the generated ASIC register header ecosystem:

- `nbio_7_0_sh_mask.h` provides only field masks and shifts.
- `nbio_7_0_offset.h` provides register offsets/addresses for the same symbolic register names where present.
- `nbio_7_0_default.h` provides reset/default values for many `smn...` registers.
- `amdgpu.h` provides the token-pasting field helpers that consume these definitions.

Direct includes of the NBIO 7.0 mask header were found in:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_0.c`
- `drivers/gpu/drm/amd/amdgpu/soc15.c`
- `drivers/gpu/drm/amd/pm/powerplay/hwmgr/smu10_inc.h`

The local tree does not contain a `nbio_7_0_d.h`; address metadata for NBIO 7.0 is represented by `nbio_7_0_offset.h` and `nbio_7_0_smn.h`.

## Integration Points

This file is part of the AMDGPU ASIC register ABI. Integration is compile-time and symbol-name based:

- NBIO initialization code can use these masks to program doorbells, PCIe features, interrupt routing, and BIF configuration registers.
- SOC15 common code includes the header so shared register manipulation macros can target NBIO 7.0 fields.
- PowerPlay/SMU code includes the header through `smu10_inc.h`, making the same field definitions available to power-management paths.
- PCIe error handling or diagnostics can interpret AER status/mask/severity fields and header/prefix log registers using these definitions.
- PCIe link training and speed handling can inspect `LINK_CAP`, `LINK_STATUS`, `LINK_CAP2`, `LINK_STATUS2`, and per-lane equalization fields.
- Virtualization and multi-function routing logic can rely on the `DEVx_EPFy` naming to address the correct endpoint/function register block.

## Risks and Edge Cases

- Bitfield drift is high impact. Any incorrect shift or mask silently corrupts field extraction/insertion in all users of `REG_GET_FIELD()` and `REG_SET_FIELD()`.
- Register-name context matters. This chunk crosses from `DEV0_EPF7` to `DEV1_EPF0` and then to `DEV1_EPF1`; using a field macro with the wrong register prefix may compile if a similarly named field exists but target the wrong function's layout.
- Several fields are reserved or capability descriptors. Driver code should avoid writing reserved bits and should preserve them during read-modify-write operations.
- AER status, mask, and severity registers have different semantics despite sharing similar field names. Confusing status bits with mask bits or severity bits can hide errors or report incorrect severity.
- MSI and MSI-X controls include enable/function-mask/table fields with 16-bit masks; code must respect register width and not assume all config fields are 32-bit.
- BAR enhanced control fields use compact masks (`BAR_INDEX`, `BAR_TOTAL_NUM`, `BAR_SIZE`). Incorrect sizing writes can affect PCI resource aperture behavior.
- DPA and power budget fields encode units/scales and selected entries. Reading `DATA` without setting or understanding `DATA_SELECT` may produce misleading power information.
- Per-lane equalization fields repeat for lanes 0-15. Mechanical copy/paste mistakes around lane numbers can cause link training diagnostics or tuning to refer to the wrong lane.
- Some covered macros have matching defaults but may not have obvious offset matches in every generated header namespace. Users need the correct `mm`, `ix`, or `smn` address symbol family for the access path they are using.

## Test Signals

Useful validation signals for this chunk are mostly compile-time and hardware-integration oriented:

- Build coverage for AMDGPU configurations that include `nbio_v7_0.c`, `soc15.c`, and SMU10 PowerPlay headers verifies that token-pasted field names resolve.
- Static checks can verify every `__SHIFT`/`_MASK` pair is internally consistent: mask width covers the shifted field and fields do not unexpectedly overlap within a register.
- Generated-header consistency checks can compare `nbio_7_0_sh_mask.h` against `nbio_7_0_offset.h` and `nbio_7_0_default.h` for register-name coverage.
- Runtime smoke tests on NBIO 7.0 hardware should monitor PCIe link status, MSI/MSI-X interrupt delivery, BAR sizing/resource assignment, AER status reporting, and power-management transitions.
- Error-injection or PCIe AER tests should confirm correct interpretation of uncorrectable/correctable status, masks, severity, and TLP header/prefix logs.
- Link training diagnostics should confirm lane error and equalization registers map correctly across all 16 lanes for `DEV1_EPF0`.

### subset-b-003115: lines 114772-117356

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 114772-117356

## Scope

This chunk is part of AMDGPU's generated NBIO 7.0 shift/mask register header. It contains 2,100 `#define` constants: 1,050 `__SHIFT` values and 1,050 `_MASK` values. There are no functions, structs, enums, global variables, allocations, locks, sysfs/debugfs handlers, or executable control-flow statements in this range.

The slice starts in the tail of the `BIF_CFG_DEV1_EPF1_2` PCIe Dynamic Power Allocation and ACS/ARI definitions, then covers a full `BIF_CFG_DEV1_EPF2_2` endpoint-function PCI configuration-space block. It continues through PF1 BIF/NBIO access windows, scratch registers, interrupt/reset/doorbell/power/BACO/HDP/mailbox controls, GDC1 doorbell and misc controls, and then repeats unprefixed PF1/SYSDEC/RCC endpoint field families. It ends inside `DN_PCIE_CNTL`; the remaining downstream-device control fields are in the following chunk.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield-description layer for NBIO 7.0 registers. For each hardware field, this file exposes:

- `<REGISTER>__<FIELD>__SHIFT`, the bit position used to encode or decode that field.
- `<REGISTER>__<FIELD>_MASK`, the mask used to isolate or preserve that field in a register value.

This chunk describes PCIe endpoint configuration and NBIF/PF control state for AMD GPU hardware, despite the broader repository path being under a Ceph-client source tree. Runtime AMDGPU code combines these macros with companion register address headers and register helpers to read, update, or decode NBIO PCIe/NBIF hardware registers.

The covered hardware roles are:

- PCIe endpoint function 2 config-space identity, BARs, power management, PCIe link/device capabilities, MSI/MSI-X, AER, enhanced BAR, power budget, DPA, ACS, and ARI fields.
- PF1 MMIO, SYSHUB, and PCIe indirect-index/data windows.
- SBIOS/BIOS scratch registers used for firmware-driver handoff or diagnostics.
- RLC, VCE, and UVD interrupt-control bits related to command completion, hang recovery, FLR needs, and VM-busy transitions.
- GFX MMIO register CAM address/remap controls and completion policy registers.
- RCC strap, endpoint, and downstream PCIe controls, including AER interrupt/status bits, LTR/DPA, requester ID, TPH disable controls, completion/error ignore policy, and link-speed straps.
- BIF PF1 bus, reset, interrupt, clock-request pad, feature, doorbell, framebuffer, busy-delay, transaction-pending, BACO, voltage/power status, HDP flush, ring-buffer, mailbox, VM/HV mailbox, and GPUIOV sizing fields.
- GDC1 doorbell range and misc controls for SDMA, IH, MMSCH, ATDMA, SDP/GDC power gating, and doorbell fences.

## Important Macro Families

The opening `BIF_CFG_DEV1_EPF1_2_*` fragment completes part of the preceding endpoint-function block. It includes PCIe DPA latency/status/control and substate power-allocation fields, ACS enhanced capability/header/capability/control bits, and ARI enhanced capability/capability/control bits. These are virtualization, peer-to-peer routing, and PCIe power-management fields; this chunk only owns their tail because the corresponding endpoint-function block starts in the previous chunk.

`BIF_CFG_DEV1_EPF2_2_*` is the largest complete family in this range. It mirrors PCI/PCIe config-space layout for device 1 endpoint function 2. It includes vendor/device IDs, command/status, revision/class, BAR1-BAR6, ROM BAR, capability pointer, interrupt line/pin, adapter IDs, vendor capability, power-management capability/status-control, USB-related SBRN/FLADJ/DBESL, PCIe capability/device/link fields, device/link second-generation fields, MSI/MSI-X capability structures, SATA capability/index/data registers, vendor-specific enhanced capabilities, AER status/mask/severity/capability/header log/TLP prefix log registers, BAR enhanced capabilities, power-budget fields, DPA fields, ACS fields, and ARI fields.

Within the `BIF_CFG_DEV1_EPF2_2_*` block, AER macros deserve special attention. `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, and `PCIE_UNCORR_ERR_SEVERITY` expose data-link protocol, poisoned TLP, completion timeout/abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, uncorrectable internal, MC blocked TLP, atomic egress blocked, TLP prefix blocked, and poisoned Egress Blocked status/policy bits. `PCIE_CORR_ERR_STATUS` and `PCIE_CORR_ERR_MASK` cover receiver error, bad TLP/DLLP, replay rollover, replay timeout, advisory non-fatal, corrected internal, and header log overflow bits. `PCIE_ADV_ERR_CAP_CNTL` and the header/TLP prefix log fields describe diagnostics and ECRC policy.

The `BIF_BX_PF1_MM_INDEX`, `BIF_BX_PF1_MM_DATA`, and `BIF_BX_PF1_MM_INDEX_HI` fields define PF1 indirect MMIO access windows. The `BIF_BX_PF1_SYSHUB_INDEX_OVLP`, `BIF_BX_PF1_SYSHUB_DATA_OVLP`, `BIF_BX_PF1_PCIE_INDEX`, `BIF_BX_PF1_PCIE_DATA`, `BIF_BX_PF1_PCIE_INDEX2`, and `BIF_BX_PF1_PCIE_DATA2` fields describe overlapping indirect access paths for SYSHUB and PCIe register spaces. These are integration points for code that must sequence index/data accesses correctly.

The SBIOS and BIOS scratch register families are full-width 32-bit fields. They do not define protocol semantics by themselves, but they provide preserved or firmware-owned storage locations that AMDGPU, BIOS, SMU, or diagnostics can use for state handoff depending on the platform flow.

`BIF_BX_PF1_BIF_RLC_INTR_CNTL`, `BIF_BX_PF1_BIF_VCE_INTR_CNTL`, and `BIF_BX_PF1_BIF_UVD_INTR_CNTL` expose four repeated interrupt conditions per block: command complete, hang self-recovered, hang needs FLR, and VM busy transition. The unprefixed `BIF_RLC_INTR_CNTL`, `BIF_VCE_INTR_CNTL`, and `BIF_UVD_INTR_CNTL` repeat the same field layout later in the chunk.

The GFX MMIOREG CAM families provide eight address/remap pairs, an enable byte, and completion-response programming fields. These fields let hardware remap selected GFX MMIO register windows or choose completion behavior. The prefixed `BIF_BX_PF1_GFX_MMIOREG_CAM_*` and later unprefixed `GFX_MMIOREG_CAM_*` groups have the same schema.

`RCC_STRAP2_RCC_DEV0_EPF0_STRAP0` and `RCC_DEV0_EPF0_STRAP0` define strap-derived device ID, revision, function enable, legacy device type, and D1/D2 support bits for device 0 function 0. These are configuration-source fields rather than ordinary driver-owned runtime policy bits.

`RCC_EP_DEV0_2_EP_PCIE_*` and later unprefixed `EP_PCIE_*` groups describe endpoint PCIe-side controls. They include scratch storage, unsupported-request reporting suppression, AER/error interrupt enables and statuses, invalid PASID handling, immediate PMI disable, hidden-register decode enables, LTR private snoop/non-snoop values and requirements, DPA substate power allocation for F1/F0, F0 DPA capability/control, PME service timer, TX relaxed/no-snoop override, TPH disable bits, requester ID, AER header-log timeout and per-function timer-expired bits, RX error-ignore policy, completion-timeout disable, PASID/prefix ignore policy, and Gen2/Gen3 link-speed strap bits.

`RCC_DWN_DEV0_2_DN_PCIE_*` and the final unprefixed `DN_PCIE_*` fragment define downstream-side scratch/control fields, including hardware-init write lock, downstream unsupported-request reporting suppression, and ignoring LTR-message unsupported requests. The chunk ends before the unprefixed `DN_PCIE_CNTL` masks are complete.

`BIF_BX_PF1_BUS_CNTL` is a broad PF1 bus-policy register. It covers PMI interrupt disables across endpoint/downstream/SWUS paths, VGA coherency disables, AZ/MC traffic-class selection, zero-byte-enable read/write enables, read-stall/write behavior, INTx deassertion behavior across D-state changes, unsupported-request override for ECRC, preceding-write stall flush policy, GSI split-read stall policy, HDP register flush VF mask enable, and VGA framebuffer zero-byte-enable policy.

PF1 reset and interrupt macros include `BIF_BX_PF1_BX_RESET_EN`, `BIF_BX_PF1_MM_CFGREGS_CNTL`, `BIF_BX_PF1_BX_RESET_CNTL`, `BIF_BX_PF1_INTERRUPT_CNTL`, and `BIF_BX_PF1_INTERRUPT_CNTL2`. These define COR/REG/STY reset enables, FLR-twice and VF-enable-low reset behavior, MM config access selection, link training enable, IH dummy-read behavior, interrupt delay, generated IH interrupts, non-snoop request policy, and dummy-read address.

PF1 doorbell and transaction fields include `BIF_BX_PF1_BIF_DOORBELL_CNTL`, `BIF_BX_PF1_BIF_DOORBELL_INT_CNTL`, `BIF_BX_PF1_BIF_FB_EN`, `BIF_BX_PF1_BIF_MST_TRANS_PENDING_VF`, `BIF_BX_PF1_BIF_SLV_TRANS_PENDING_VF`, and `BIF_BX_PF1_BIF_TRANS_PENDING`. These macros affect self-ring behavior, translation checks, doorbell monitor interrupts, framebuffer read/write enable, and pending master/slave transaction status for PF/VF traffic.

The BACO and power/voltage families include `BIF_BX_PF1_BACO_CNTL`, `BIF_BX_PF1_BIF_BACO_EXIT_TIME0`, `BIF_BX_PF1_BIF_BACO_EXIT_TIMER1..4`, `BIF_BX_PF1_MEM_TYPE_CNTL`, `BIF_BX_PF1_SMU_BIF_VDDGFX_PWR_STATUS`, and `BIF_BX_PF1_BIF_VDDGFX_*` threshold registers. These describe bus active/chip off policy, BACO exit timing, memory-type control, and SMU/BIF VDDGFX threshold/status fields used by power-management flows.

`BIF_BX_PF1_BIF_DOORBELL_GBLAPER1_*` and `BIF_BX_PF1_BIF_DOORBELL_GBLAPER2_*` define global doorbell aperture bounds. `BIF_BX_PF1_DOORBELL_SELFRING_GPA_APER_*` defines GPA aperture base and enable/mode/size for doorbell self-ring. These are address-range definitions for doorbell routing and virtualization-sensitive aperture control.

`BIF_BX_PF1_GPU_HDP_FLUSH_REQ` and `BIF_BX_PF1_GPU_HDP_FLUSH_DONE` expose one bit each for CP0-CP9 and SDMA0-SDMA1 flush request/done. `BIF_BX_PF1_REMAP_HDP_MEM_FLUSH_CNTL`, `BIF_BX_PF1_REMAP_HDP_REG_FLUSH_CNTL`, `BIF_BX_PF1_HDP_REG_COHERENCY_FLUSH_CNTL`, and `BIF_BX_PF1_HDP_MEM_COHERENCY_FLUSH_CNTL` identify flush-remap or coherency flush controls. These macros are directly relevant to cache/coherency barriers around GPU command processors and SDMA.

The `BIF_BX_PF1_BIF_RB_*` group defines a BIF ring-buffer base, read pointer, write pointer, write-pointer address, and overflow indication. The mailbox groups define transmit and receive message-buffer dwords, valid/ack control bits, interrupt enables, and a compact VM/HV mailbox with 4-bit data fields and valid/ack/intr bits. These are hardware communication primitives rather than software queues owned by the header.

`BIF_BX_PF1_BIF_BME_STATUS` and `BIF_BX_PF1_BIF_ATOMIC_ERR_LOG` cover DMA-on-BME-low and unsupported atomic-operation diagnostics with explicit clear bits. The GPUIOV sizing macros for UVD, VCE, and GFX/SDMA expose per-block configuration sizing fields used by GPU virtualization support.

The `GDC1_*` block covers GDC1 SDP disconnect hysteresis, non-PF MMREG request set-error suppression, SDMA0/SDMA1/IH/MMSCH doorbell range offset and size, ATDMA weighted arbitration and read insertion, doorbell fence enable, S2A doorbell 64-bit support disables, AXI host completion endpoint disable, and GDC power-gating reset selection.

## APIs, Types, And Functions

This chunk exports only C preprocessor constants. There are no callable APIs and no C types. The practical interface is the generated macro namespace used by AMDGPU register helpers.

Consumers generally pair these constants with:

- Register address symbols from `nbio_7_0_offset.h`.
- Reset/default symbols from `nbio_7_0_default.h`.
- SMN address symbols from `nbio_7_0_smn.h` where applicable.
- AMDGPU register helpers such as `REG_SET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, indirect-index/data helpers, or direct bit masking and shifting.

The macros do not encode register access type, reset value, reserved-bit policy, side-effect semantics, timing requirements, or hardware ownership. A caller must know whether a field is read-only, write-one-to-clear, sticky, strap-derived, firmware-owned, reset-sensitive, or safe for read/modify/write.

## Control Flow

There is no local software control flow in this header. Runtime flow is external:

1. AMDGPU or related code chooses a register address from the companion NBIO 7.0 address metadata.
2. The code reads or composes a 32-bit register value through MMIO, PCIe config, SMN, SYSHUB, or indirect index/data access.
3. It extracts or updates fields using the `__SHIFT` and `_MASK` values in this chunk.
4. Hardware state machines then act on the resulting field values.

The implicit hardware workflows represented here include PCIe enumeration and capability reporting, endpoint power management, DPA substate accounting, ACS/ARI virtualization behavior, AER error logging and masking, MSI/MSI-X programming, PF1 reset and FLR-related behavior, GPU hang/VM-busy interrupt signaling, doorbell aperture routing, HDP coherency flush request/done handshakes, BACO entry/exit timing, endpoint/downstream PCIe RX/TX error policy, link-speed strap interpretation, mailbox valid/ack handshakes, and GDC1 doorbell range setup.

Indirect access windows have sequencing constraints even though the macros are static. Index registers must be programmed before reading or writing their paired data registers, and concurrent or stale index use can target the wrong hardware register. The header does not provide locking or ordering.

## State And Persistence Behavior

The file itself owns no software state and persists nothing. It describes hardware-visible state in NBIO/NBIF/PCIe/GDC registers.

Represented state categories include:

- PCI config-space identity, capability, BAR, interrupt, and power-management fields.
- PCIe AER, ACS, ARI, DPA, MSI, MSI-X, link, and device control/status bits.
- Strap-derived device ID, revision, function-enable, and power-state support fields.
- Scratch registers and BIOS/SBIOS handoff fields.
- Interrupt enable/status bits for PCIe/AER, RLC, VCE, UVD, doorbell monitor, IOHC RAS, mailbox, and VM/HV mailbox paths.
- Reset, FLR, link-training, and D-state sensitive control fields.
- Doorbell ranges and apertures, including self-ring and global aperture bases.
- HDP flush request/done and coherency flush controls.
- BACO, VDDGFX, memory-type, and power-status fields.
- Ring-buffer, mailbox, transaction-pending, atomic-error, BME, and GPUIOV state.
- GDC1 doorbell, SDP, ATDMA arbitration, and power-gating controls.

Persistence depends on hardware reset domain, PCIe hot/cold reset, FLR, BACO, suspend/resume, power gating, firmware initialization, BIOS handoff, and explicit driver writes. Many status and diagnostic fields are likely sticky or clear-on-write according to hardware semantics, but this shift/mask header does not declare those semantics. Full-width masks such as `0xFFFFFFFFL` identify field width only; they are not evidence that arbitrary writes are safe.

## Dependencies And Integration Points

The direct dependency is the generated AMD NBIO 7.0 register database. This header must remain synchronized with the companion NBIO 7.0 offset, default, and SMN headers. In this tree, `nbio_v7_0.c`, `soc15.c`, and PowerPlay's `smu10_inc.h` include `nbio_7_0_sh_mask.h` with the adjacent NBIO 7.0 generated headers.

Important AMDGPU integration points include:

- NBIO v7.0 initialization, memory-controller access enabling, and register remapping.
- Doorbell setup for SDMA, VCN/MMSCH, IH, self-ring, and global aperture routing.
- HDP flush register discovery and request/done polling for CP and SDMA engines.
- PCIe capability, AER, MSI/MSI-X, power-management, and link-management handling around Linux PCI core interactions.
- GPU reset, FLR, hang recovery, transaction-pending, and D-state/BACO flows.
- Runtime power management, LTR/DPA/PME, VDDGFX threshold/status, and GDC power-gating behavior.
- Virtualization and isolation paths involving ACS/ARI, GPUIOV sizing, PF/VF doorbell apertures, BME status, atomic error logging, VM/HV mailbox, and indirect MMIO/SYSHUB/PCIe register access.
- Firmware and BIOS handoff through strap and scratch registers.

The repeated prefixed and unprefixed families are a generated-addressing detail: both sets describe similar PF1/SYSDEC/RCC/GDC register schemas in different address blocks or access paths. Consumers must use the macro family that matches the selected register address.

## Risks And Edge Cases

- A wrong shift or mask can compile cleanly while corrupting unrelated hardware bits. In this chunk that can affect PCIe enumeration, BAR reporting, AER policy, ACS/ARI isolation, MSI/MSI-X interrupt delivery, doorbell routing, HDP flush handshakes, BACO timing, or reset behavior.
- The chunk begins and ends on logical block boundaries that are incomplete. The `BIF_CFG_DEV1_EPF1_2` DPA/ACS/ARI block starts in the previous chunk, and the unprefixed `DN_PCIE_CNTL` masks continue in the next chunk.
- Status, enable, mask, and clear bits often share similar names. Using a status mask against a control register, or treating clear bits as persistent status, can drop diagnostics or create interrupt storms.
- AER and atomic/BME error-log fields may have sticky or write-one-to-clear semantics. Software must preserve evidence long enough for diagnostics while also clearing conditions according to the hardware contract.
- Indirect MMIO/SYSHUB/PCIe index/data windows are shared access mechanisms. Missing synchronization or stale indexes can read or write the wrong register.
- Doorbell aperture and self-ring GPA fields are security- and virtualization-sensitive because they define address windows for queue signaling. Bad aperture size/base/mode values can route doorbells incorrectly or expose guest/host signaling paths.
- HDP flush request/done bits are synchronization primitives for command processors and SDMA engines. Polling the wrong bit, failing to wait, or misprogramming remap/coherency controls can leave stale CPU/GPU-visible data.
- BACO, DPA, LTR, PME, D-state, VDDGFX, and power-gating fields intersect with suspend/resume and runtime power management. Incorrect programming can produce devices that enumerate but fail during resume, link power transitions, or reset recovery.
- Generated families are highly repetitive. Copy or generation drift across `BIF_CFG_DEV1_EPF2_2`, `RCC_EP_DEV0_2_EP_PCIE_*`, unprefixed `EP_PCIE_*`, and prefixed/unprefixed PF1 blocks can be hard to catch by review alone.

## Test And Validation Signals

- Build AMDGPU with NBIO 7.0 support enabled. Missing or renamed symbols referenced by `nbio_v7_0.c`, `soc15.c`, PowerPlay, or related register code should fail at compile time.
- Run generated-header consistency checks: every field should have one `__SHIFT` and one `_MASK`, masks should align with shifts and width expectations, full-width fields should be intentional, and repeated prefixed/unprefixed register schemas should match where hardware expects them to.
- Cross-check this chunk against `nbio_7_0_offset.h` and `nbio_7_0_default.h` so every register family has a matching address/default entry and no field stems drift from the generated database.
- On NBIO 7.0 hardware, validate PCIe enumeration for endpoint function 2: IDs, class/revision, BAR sizing, capability list traversal, MSI/MSI-X capability behavior, AER capability data, ACS/ARI exposure, DPA/power budget fields, and link/device capability/status reports.
- Exercise GPU reset, PF/VF FLR, suspend/resume, BACO entry/exit, D3/D0 transitions, and runtime power management while checking transaction-pending bits, reset/link-training behavior, PME/LTR/DPA status, and post-reset PCIe responsiveness.
- Stress command processors and SDMA while tracing HDP flush request/done bits for CP0-CP9 and SDMA0-SDMA1. Flush done bits should correspond to the intended request bits and no stale-data symptoms should appear.
- Validate doorbell programming for SDMA, IH, MMSCH/VCN, self-ring, and global apertures. Doorbell ranges should match expected offsets/sizes and guest/host isolation should hold under SR-IOV or GPUIOV scenarios.
- Inject or observe PCIe/AER/RAS-like errors where supported and verify interrupt enable/status bits, correctable/uncorrectable status/mask/severity, header/TLP prefix logging, atomic error logs, BME status, and clear behavior.
- Exercise mailbox and VM/HV mailbox handshakes by checking valid/ack transitions and interrupt enables. Lost valid/ack transitions indicate bad bit definitions or ordering.
- Validate GDC1 doorbell ranges, ATDMA arbitration settings, SDP disconnect hysteresis, and GDC power-gating reset behavior under traffic stress and suspend/resume.

## Cross-Chunk Notes

This report covers only lines 114772-117356. The previous chunk owns the beginning of the `BIF_CFG_DEV1_EPF1_2` DPA/ACS/ARI endpoint-function block. The next chunk owns the rest of unprefixed downstream-device PCIe control fields after `DN_PCIE_CNTL`. The merge/reconciliation lane should combine adjacent chunks before making whole-file claims about either boundary block.

### subset-b-003116: lines 117357-118975

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_sh_mask.h lines 117357-118975

## Scope

This chunk is a generated AMDGPU NBIO 7.0 shift/mask header segment. It contains 1,364 `#define` field-layout macros, 229 register comments, and 8 address-block comments. There are no functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts in the tail of a downstream PCIe-control group, covering `DN_PCIE_CNTL` leftovers plus `DN_PCIE_CONFIG_CNTL`, `DN_PCIE_RX_CNTL2`, `DN_PCIE_BUS_CNTL`, and `DN_PCIE_CFG_CNTL`. It then covers RCC downstream/PF/VF decode fields, BIF PF and PF/VF decode fields, GDC fields, a small GFX MSI-X table block, and the end of the `syshub_mmreg_ind_syshubind` field definitions. The chunk ends at the file trailer `#endif`, so this is the final slice of `nbio_7_0_sh_mask.h`.

## Purpose

`nbio_7_0_sh_mask.h` is the bitfield half of AMDGPU's generated NBIO 7.0 register interface. For each hardware register field, it exports:

- `<REGISTER>__<FIELD>__SHIFT`, the least-significant bit position for encoding or decoding the field.
- `<REGISTER>__<FIELD>_MASK`, the bit mask used to isolate, clear, preserve, or update the field.

This slice describes NBIO, BIF, RCC, GDC, MSI-X, doorbell, mailbox, HDP coherency, GPU virtualization, and system-hub clock/QoS/register-interconnect fields. Despite the repository path being under a Ceph client source mirror, this chunk is GPU PCIe/NBIO register metadata and has no filesystem behavior.

## Important Macro Families

The opening downstream PCIe and `nbio_nbif0_rcc_dwnp_dev0_BIFDEC1` groups define fields for PCIe error reporting, receiver error-ignore policy, link-speed strap enables, link-bandwidth notification disable, multifunction strap state, LTR message capture, hidden config-register decode enables, FLR extension mode, immediate PMI disable, and AER completion-timeout reporting controls. These are low-level PCIe policy knobs used by code that configures or diagnoses downstream/root-complex behavior.

The `nbio_nbif0_rcc_dev0_BIFPFVFDEC1` group covers RCC per-function or SR-IOV-visible state: invalid SR-IOV register access and doorbell-read access status, doorbell aperture enable, configuration memory size/reserved fields, and `RCC_IOV_FUNC_IDENTIFIER` fields for function identity and IOV enable state.

The main `nbio_nbif0_rcc_dev0_BIFDEC1` group describes RCC control-plane state. It includes invalid-SRIOV-access interrupt enable, BACO ROM/AZ request disables, DB aperture reset enable, vendor-defined message support, peer-register ranges, bus-control bits for PMI, root error logging, poisoned completion logging, downstream completion error handling, privileged max payload and max read request size, VGA/config aperture controls, F0/config aperture bases and sizes, XDMA aperture bounds, feature-control knobs for unsupported-request, poison, PASID, page request, invalid completion, MSI pending clearing, BME checks, ECRC, and host-poison behavior. It also defines bus-number list/capture fields, host bus number, peer frame-buffer offsets, common link control, endpoint requester-ID restore, LTR local-switch latency, and multi-host arbitration controls.

The `nbio_nbif0_bif_bx_pf_BIFDEC1` group is the largest BIF PF register block in this slice. It defines MM indirect-access disable, BIF bus controls for PMI interrupts, VGA coherency, traffic class selection, zero-byte-enable accesses, interrupt deassertion behavior, ECRC/UR handling, read/write stall and HDP flush policies, scratch registers, reset enables, MM-to-config access selection, link-training enable, IH interrupt dummy-read and delay controls, CLKREQB pad controls, BIF feature-control bits, doorbell controls and interrupts, frame-buffer enable, busy-delay counter, VF master/slave transaction-pending status, BACO controls and exit timers, memory type control, VDDGFX range and compare registers, global doorbell aperture bounds, remapped HDP flush controls, BIF ring-buffer control/base/read/write pointer fields, mailbox index, GPUIOV config sizes for UVD/VCE/GFX/SDMA, PERSTB/PX/REFPAD/CLKREQB pad controls.

The `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` group adds status and virtualization-facing controls. It includes bus-master-enable violation status/clear, atomic unsupported-request error logs and clears, self-ring GPA doorbell aperture base/control fields, HDP register and memory coherency flush controls, per-engine `GPU_HDP_FLUSH_REQ` and `GPU_HDP_FLUSH_DONE` bits for CP0 through CP9 and SDMA0/SDMA1, BIF master/slave transaction-pending state, 4-dword transmit and receive mailbox message buffers, mailbox valid/ack handshakes, mailbox interrupt enables, and compact VM/HV mailbox data/valid/ack/intr fields.

The `nbio_nbif0_gdc_GDCDEC` group defines GDC and doorbell routing metadata. It includes SDP disconnect hysteresis, SHUB MMREG request error behavior for non-PF requests, reserved registers, SOCCLK-specific SDP hysteresis, doorbell ranges for SDMA0, SDMA1, IH, and MMSCH0, ATDMA arbitration and VC weights, doorbell-fence enable, 64-bit doorbell support disables for SDMA and CP, AXI host completion disable, and GDC power-gating reset selection.

The `nbio_nbif0_rcc_dev0_BIFDEC2` group defines three GFX MSI-X vector table entries: low/high message address, message data, per-vector mask bit, and pending bits in the MSI-X pending bit array. These fields model hardware-backed interrupt vector storage rather than Linux-side MSI descriptor objects.

The final `syshub_mmreg_ind_syshubind` group describes system-hub indirect MMREG fields. It defines SOCCLK and SHUBCLK deep-sleep allow enables for host and DMA client lanes, deep-sleep timers, bgen enhancement bypass/immediate enables, per-switch DMA QoS min/max controls, repeated per-client reset/QoS/static override/read-weight/write-weight controls, host client reset behavior, clock-gating controls, transaction-idle status, HP timer, MGCG controls, CPF doorbell reset behavior, scratch and client-mask fields, and NIC400 ASIB/AMIB read/write issuing-override fields across several fabric instances.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated C preprocessor macro namespace.

Consumers combine these constants with sibling NBIO 7.0 register address/default/access headers and AMDGPU register helpers. Typical use is to read a register, extract a field with `*_MASK` and `*_SHIFT`, or compose a read/modify/write value by clearing the mask and ORing `(value << shift) & mask`. The macros do not encode register addresses, access permissions, reset values, reserved-bit policy, write-one-to-clear semantics, required polling intervals, or firmware ownership.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. AMDGPU code selects a BIF/RCC/GDC/SYSHUB register address from companion generated metadata.
2. It accesses that register through MMIO, config-space, SMN, or an indirect MMREG path appropriate to the block.
3. It uses the shift/mask macros in this chunk to decode status or build a read/modify/write update.
4. Hardware state machines then carry out PCIe error handling, FLR/reset sequencing, doorbell routing, HDP flush handshakes, mailbox valid/ack exchanges, MSI-X delivery, BACO entry/exit timing, power/clock gating, QoS arbitration, or system-fabric transaction control.

Several represented flows are asynchronous and require sequencing by consumers: `GPU_HDP_FLUSH_REQ` must be matched against `GPU_HDP_FLUSH_DONE`; mailbox transmit/receive buffers require valid/ack transitions; BIF ring-buffer pointers and overflow status require ownership discipline; reset and FLR fields interact with transaction-pending status; BACO timer/control fields affect power-state transitions; and SYSHUB deep-sleep/MGCG/QoS controls interact with fabric idleness.

## State And Persistence Behavior

The header owns no mutable software state and persists nothing. It describes hardware-visible state in NBIO 7.0 registers.

Represented state includes writable configuration bits, strap-derived state, interrupt status and clear bits, error logs, transaction-pending status, scratch registers, reset enables, timer values, address aperture bases/ranges, mailbox payload dwords, valid/ack handshakes, ring-buffer read/write pointers, per-engine HDP flush request/done flags, MSI-X address/data/mask/pending fields, power-gating/clock-gating controls, QoS weights and static overrides, and NIC400 issuing behavior.

Persistence is determined by the hardware reset and power domains, not by this file. Some fields likely reset on cold reset, hot reset, FLR, BACO, link reset, or GDC/SYSHUB power gating; others may be firmware-initialized, sticky until explicitly cleared, or live status. The shift/mask macros do not reveal which fields are sticky, clear-on-write, clear-on-read, shadowed, virtualized per function, or preserved across suspend/resume.

## Dependencies And Integration Points

This generated file depends on AMD's NBIO 7.0 register database and must stay synchronized with sibling offset, default-value, and access metadata. Address comments group related registers, but this file itself only provides bit positions and masks.

AMDGPU integration points include NBIO/BIF initialization, PCIe bring-up and policy setup, SR-IOV/GPUIOV virtualization, VF/PF register decode and invalid-access handling, doorbell aperture programming, HDP coherency flush paths, interrupt handler ring-buffer setup, MSI/MSI-X programming, VM/HV mailbox protocols, BACO and runtime power management, GPU reset/FLR/link reset handling, and system-hub clock, deep-sleep, QoS, and fabric issuing configuration.

Linux integration is indirect but important. MSI-X fields correspond to interrupt delivery state coordinated with the PCI/MSI core. Doorbell, HDP flush, and mailbox fields are used by command submission, interrupt, virtualization, and reset paths. PCIe error reporting, AER, LTR, FLR, BME, and max-payload/max-read-request fields intersect with Linux PCI core assumptions and platform firmware setup.

## Risks And Edge Cases

- Generated shift/mask drift can compile cleanly while programming the wrong bit, causing broken PCIe error policy, invalid SR-IOV isolation, failed doorbells, lost interrupts, stale HDP data, reset hangs, or bad power-gating behavior.
- This chunk starts in the middle of a downstream PCIe control group. Whole-file research must reconcile the previous chunk before treating the opening `DN_PCIE_CNTL` context as complete.
- Status and clear fields share registers in several places, including BIF doorbell interrupts, BME status, atomic error logs, and ring-buffer overflow. Consumers must know access semantics before writing masks.
- Full-width masks such as mailbox payloads, scratch registers, aperture high/low values, MSI-X message data, and reserved fields are not blanket permission to overwrite all bits. Ownership, alignment, firmware programming, and reserved-bit preservation still matter.
- Doorbell aperture, range, and self-ring GPA fields affect CPU/GPU notification paths. Incorrect base, size, 48-bit checking, or translation policy can misroute writes or expose isolation bugs under SR-IOV.
- HDP flush request/done fields are synchronization points. Missing polling, wrong engine bit selection, or timeout mistakes can leave CPU-visible memory stale or stall command submission/reset paths.
- Mailbox valid/ack fields can deadlock if either side reuses buffers before acknowledgements or enables interrupts without clearing stale state.
- MSI-X address/data/mask/pending fields must remain consistent with PCI/MSI core ownership; direct hardware programming that races Linux vector setup can drop or misdirect interrupts.
- Reset, FLR, transaction-pending, and BACO fields are order-sensitive and can race with runtime PM, suspend/resume, firmware ownership, and in-flight DMA.
- SYSHUB deep-sleep, MGCG, QoS, and NIC400 issuing overrides can affect fabric ordering and latency. Aggressive power or QoS settings need validation under graphics, DMA, display, interrupt, and virtualization loads.

## Test Signals

- Build AMDGPU with NBIO 7.0 support enabled. Compile-time references catch missing, renamed, or malformed generated symbols used by consumers.
- Run generated-header consistency checks: every field should have a coherent `__SHIFT`/`_MASK` pair, masks should fit the intended register width, repeated CP/SDMA/QoS/client-lane patterns should be complete, and register comments should map to sibling address metadata.
- Cross-check this final header chunk against NBIO 7.0 offset/default/access headers so PF, PF/VF, GDC, MSI-X, and SYSHUB registers have matching addresses and reset values.
- On supported hardware, validate cold boot, warm reboot, suspend/resume, BACO entry/exit, FLR, GPU reset, link reset, SR-IOV VF enable/disable, and transaction-pending drain behavior.
- Exercise doorbell paths for CP, SDMA, IH, MMSCH, self-ring GPA apertures, and 64-bit doorbell support; verify invalid or non-PF accesses are logged or blocked as expected.
- Validate HDP coherency by issuing per-engine flush requests and checking `GPU_HDP_FLUSH_DONE` bits before reading CPU-visible data.
- Exercise mailbox transmit/receive paths, valid/ack interrupts, and VM/HV mailbox fields under normal operation and reset recovery.
- Validate MSI-X vector programming and pending/mask behavior through Linux interrupt tests, including masking, unmasking, and pending-bit observation.
- Stress SYSHUB power/QoS settings with concurrent graphics, SDMA, interrupts, virtualization, and power-management transitions while watching for hangs, latency spikes, or fabric idle-status mismatches.
