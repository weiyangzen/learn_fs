# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 56613-59036

## Scope

This chunk is a generated AMD NBIO 2.3 shift/mask header slice. It contains C preprocessor constants only: no functions, structs, variables, dynamic allocation, locking, software persistence, or executable control flow. The macros define bit offsets and bit masks for NBIO/BIF PCIe configuration-space registers.

The range starts in the middle of `BIF_CFG_DEV0_SWDS0_LINK_CNTL`, after the earlier `PM_CONTROL`, `READ_CPL_BOUNDARY`, `LINK_DIS`, `RETRAIN_LINK`, `COMMON_CLOCK_CFG`, and `EXTENDED_SYNC` shift definitions from the previous chunk. It then covers the rest of the `BIF_CFG_DEV0_SWDS0_*` PCIe downstream-switch/device configuration decode, including PCIe capability 2, MSI, SSID, vendor-specific capability, virtual-channel, device serial number, AER, secondary PCIe, ACS, DLF, 16GT PHY, equalization, and PCIe margining definitions.

The chunk then enters two SR-IOV virtual-function address blocks:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf0_bifcfgdecp`, covering a complete `BIF_CFG_DEV0_EPF0_VF0_0_*` PCI config-space image from vendor/device IDs through ATS and ARI enhanced capabilities.
- `nbio_nbif0_bif_cfg_dev0_epf0_vf1_bifcfgdecp`, covering the start of `BIF_CFG_DEV0_EPF0_VF1_0_*` from vendor/device IDs through the first part of `PCIE_UNCORR_ERR_STATUS`.

The range ends at `BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_STATUS__ECRC_ERR_STATUS__SHIFT`. The remaining `VF1` uncorrectable-error status masks and following AER/VF1 capability fields continue in the next chunk. In total this slice contains 2,142 `#define` lines: 1,073 `__SHIFT` macros and 1,069 `_MASK` macros.

Although the repository path is under a local `ceph-client` mirror, this file is AMDGPU hardware metadata. It does not implement Ceph or distributed filesystem behavior.

## Purpose

`nbio_2_3_sh_mask.h` publishes the bitfield ABI for AMD NBIO 2.3 registers. Each register field is represented by generated preprocessor constants:

- `<REGISTER>__<FIELD>__SHIFT` gives the bit offset for packing or extracting a field.
- `<REGISTER>__<FIELD>_MASK` gives the mask used to isolate or preserve that field.

This chunk focuses on PCIe configuration and capability bitfields for one downstream-switch/device block (`SWDS0`) and the first virtual-function endpoint-function blocks (`EPF0_VF0_0` and part of `EPF0_VF1_0`). Runtime AMDGPU code combines these constants with matching register offsets from `nbio_2_3_offset.h` and reset/default values from `nbio_2_3_default.h`. Callers typically use helpers such as `REG_SET_FIELD`, `REG_GET_FIELD`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, and `SOC15_REG_OFFSET`.

The macros are not policy by themselves. They are the generated contract that lets NBIO, BIF, PCIe, SR-IOV, mailbox, reset, interrupt, and error-handling code address the correct bits when programming or decoding hardware state.

## Important Macro Families

### SWDS0 PCIe Link, Slot, And Device Capability Fields

The opening macros complete `BIF_CFG_DEV0_SWDS0_LINK_CNTL` and then cover `LINK_STATUS`, `SLOT_CAP`, `SLOT_CNTL`, and `SLOT_STATUS`. These fields map standard PCIe link and slot semantics: current link speed, negotiated width, link training, slot clock, data-link active state, bandwidth-management status, hotplug and attention-button controls, power-controller and indicator controls, presence detect, electromechanical interlock state, and data-link state change reporting.

`BIF_CFG_DEV0_SWDS0_DEVICE_CAP2`, `DEVICE_CNTL2`, and `DEVICE_STATUS2` expose PCIe Capability 2 fields such as completion timeout support/value/disable, ARI forwarding, AtomicOp routing/request/egress blocking, ID-based ordering, LTR enablement, emergency power reduction, ten-bit tags, OBFF, end-to-end TLP prefix support/blocking, and function readiness support. `DEVICE_STATUS2` is reserved in this generated description.

`BIF_CFG_DEV0_SWDS0_LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2` cover supported link speeds, crosslink support, lower SKP ordered-set generation/receive support, RTM presence detection, DRS-related fields, target link speed, compliance entry, hardware autonomous speed disable, de-emphasis, transmit margin, 8GT equalization phases, link equalization requests, downstream component presence, and DRS message receipt.

The chunk also defines reserved `SLOT_CAP2`, `SLOT_CNTL2`, and `SLOT_STATUS2` masks, making clear that those register slots exist in the generated config-space layout even though their fields are reserved here.

### SWDS0 MSI, SSID, Vendor-Specific, And Virtual Channel Capabilities

`BIF_CFG_DEV0_SWDS0_MSI_*` defines the MSI capability list entry, message-control bits, low/high message address fields, and 32-bit/64-bit message-data fields. The control field includes MSI enable, multi-message capability, multi-message enable, 64-bit capable indication, and per-vector masking capability.

`BIF_CFG_DEV0_SWDS0_SSID_*` describes subsystem vendor and subsystem ID fields. The vendor-specific enhanced capability macros define the enhanced-capability header, vendor-specific header (`VSEC_ID`, `VSEC_REV`, `VSEC_LENGTH`), and two full-width scratch payload registers.

The virtual-channel block covers `PCIE_VC_ENH_CAP_LIST`, port VC capability/control/status, and VC0/VC1 resource capability/control/status. These fields expose extended VC counts, low-priority VC counts, arbitration table entry sizes and offsets, VC arbitration selection/loading, TC-to-VC mapping, port arbitration selection/loading, VC ID, VC enable, and VC negotiation pending. These definitions are relevant to traffic-class and virtual-channel negotiation or diagnostics.

### SWDS0 AER, Secondary PCIe, ACS, DLF, 16GT PHY, And Margining

The AER section starts with `PCIE_ADV_ERR_RPT_ENH_CAP_LIST` and covers uncorrectable error status, mask, and severity fields for DLP, surprise down, poisoned TLP, flow control, completion timeout, completion abort, unexpected completion, receiver overflow, malformed TLP, ECRC, unsupported request, ACS violation, internal error, multicast blocked TLP, AtomicOp egress blocked, and TLP prefix blocked errors.

Correctable error status and mask fields cover receiver errors, bad TLP/DLLP, replay timer timeout, advisory non-fatal, corrected internal error, header-log overflow, and virtual-function AER message number. `PCIE_ADV_ERR_CAP_CNTL` exposes first error pointer, ECRC generation/check capability and enable bits, multiple header recording capability/enable, TLP prefix log presence, and completion timeout logging capability. The header log and TLP prefix log registers are full-width payload fields.

The secondary PCIe section defines the enhanced-capability header, `LINK_CNTL3` perform-equalization/control bits, lane error status, and per-lane 8GT equalization controls for lanes 0-15. Each lane has downstream-port TX preset, downstream-port RX preset hint, upstream-port TX preset, upstream-port RX preset hint, and reserved fields.

The ACS section defines source validation, translation blocking, P2P request/completion redirect, upstream forwarding, P2P egress control, direct translated P2P, and egress-control vector size capability/control fields. These fields are security and isolation sensitive in virtualized or peer-to-peer topologies.

The DLF section defines local/remote Data Link Feature support, exchange-enable, and valid-status fields. The 16GT PHY section defines a PCIe PHY enhanced-capability header, reserved link cap/control fields, 16GT link equalization-complete/phase/request status bits, local/RTM parity mismatch status, and per-lane 16GT downstream/upstream TX preset fields for lanes 0-15.

The PCIe margining section defines the margining enhanced-capability header, port capability/status, and per-lane margining control/status pairs for lanes 0-15. Each lane exposes receiver number, margin type, usage model, and payload fields. These definitions matter for PCIe link diagnostics and margining workflows.

### VF0 PCI Configuration Space

The `BIF_CFG_DEV0_EPF0_VF0_0_*` block defines a full PCI configuration-space bitfield map for virtual function 0 under endpoint function 0. It starts with standard PCI header fields: vendor ID, device ID, command, status, revision, programming interface, subclass, base class, cache-line size, latency timer, header type/device type, BIST, six BARs, CardBus CIS pointer, subsystem adapter ID, ROM base address, capability pointer, interrupt line/pin, minimum grant, and maximum latency.

The VF0 command/status fields expose I/O access, memory access, bus master, special cycle, memory write invalidate, PAL snoop, parity error response, stepping, SERR, fast back-to-back, interrupt disable, immediate readiness, interrupt status, capability-list presence, parity and abort status, and DEVSEL timing. `DEVICE_CNTL` includes the normal PCIe error enable bits, relaxed ordering, max payload size, extended tag, phantom function, auxiliary power PM, no-snoop, max read request size, and `INITIATE_FLR`. The associated `DEVICE_CAP` includes FLR capability and payload/latency/power fields.

VF0 then mirrors the PCIe link capability/control/status and capability-2 families seen in SWDS0: link speed/width, ASPM/latency/power/link-bandwidth fields, link disable/retrain/common-clock/extended-sync bits, link status/training fields, completion timeout, ARI, AtomicOp, IDO, LTR, OBFF, ten-bit tag, TLP prefix, emergency power, and 8GT equalization status.

Interrupt-related VF0 definitions cover MSI and MSI-X capability list entries, message-control fields, message address/data fields, MSI mask/pending and 64-bit variants, MSI-X table size, function mask, MSI-X enable, MSI-X table BIR/offset, and MSI-X pending bit array BIR/offset.

VF0 vendor-specific and AER sections define the VSEC header/scratch registers, AER enhanced-capability header, uncorrectable error status/mask/severity, correctable status/mask, AER capability/control, full-width header logs, and TLP prefix logs. The VF0 block ends with ATS and ARI enhanced capabilities: ATS invalidate queue depth, page-aligned request, global invalidate support, STU, ATC enable, ARI MFVC/ACS function group capability and enables, next function number, and function group fields.

### VF1 PCI Configuration Space Start

The `BIF_CFG_DEV0_EPF0_VF1_0_*` block repeats the same generated PCI/VF pattern as VF0 from vendor ID through MSI-X, vendor-specific capability, and the AER enhanced-capability header. The fields covered in this chunk include standard PCI command/status/header/BAR/class/capability fields; PCIe device/link capability/control/status fields; capability-2 fields; MSI/MSI-X programming fields; vendor-specific capability fields; and the first ten uncorrectable-error status shift definitions.

The chunk stops before the matching `VF1` `PCIE_UNCORR_ERR_STATUS` masks and before the `UNSUPP_REQ`, `ACS_VIOLATION`, `UNCORR_INT_ERR`, `MC_BLOCKED_TLP`, `ATOMICOP_EGRESS_BLOCKED`, and `TLP_PREFIX_BLOCKED` status shifts. Any final file-level report must join this chunk with the following one before claiming complete VF1 AER coverage.

## Control Flow

There is no runtime control flow in this header. Runtime control belongs to AMDGPU and Linux PCI/PCIe code that includes the generated NBIO headers. The usual sequence is:

1. Select a register offset from `nbio_2_3_offset.h` or a local NBIO/BIF address table.
2. Read a 16-bit or 32-bit register image through an AMDGPU register helper or prepare a value for writing.
3. Use the `__SHIFT` and `_MASK` constants, usually through `REG_GET_FIELD` or `REG_SET_FIELD`, to decode or update a field.
4. Write the value back, poll status, handle an interrupt/error, or expose decoded state to PCIe, SR-IOV, reset, RAS, or diagnostic logic.

Because these are plain macros, the compiler does not enforce that a field macro is used with the correct register, access width, side-effect model, or PF/VF ownership context.

## State And Persistence Behavior

This file stores no software state and persists nothing. It describes hardware register fields whose actual state is maintained by the GPU, PCIe link, firmware, host driver, guest driver, hypervisor, and Linux PCI infrastructure.

The represented state includes PCI command/status bits, link training/status, slot hotplug/status, MSI and MSI-X programming state, subsystem IDs, vendor-specific scratch payloads, virtual-channel arbitration and negotiation state, device serial number payloads, AER status/mask/severity/log state, ACS controls, data-link feature exchange state, PCIe Gen4/16GT equalization and parity state, PCIe margining command/status payloads, ATS/ARI controls, and VF FLR-related command bits.

Some fields are durable configuration until reset or reprogramming, such as max payload size, max read request size, MSI/MSI-X message address/data, ACS controls, VC mappings, ATS enable, and ARI controls. Others are hardware-owned or transient status, such as link training, equalization phase completion, data-link active, AER status/logs, MSI pending bits, margining ready/status, parity mismatch status, and transaction/error flags. The header does not encode read-only/write-only status, write-one-to-clear behavior, self-clearing command bits, polling requirements, reset defaults, ordering constraints, or guest-versus-host ownership rules.

## Dependencies And Integration Points

This chunk depends on the generated NBIO 2.3 register database staying synchronized across companion headers:

- `nbio_2_3_offset.h` maps the same register names to offsets/base indices.
- `nbio_2_3_default.h` maps the same register names to reset/default values.
- `nbio_2_3_sh_mask.h` maps the fields within each register.

AMDGPU NBIO/BIF code, PCIe link management, interrupt setup, SR-IOV virtualization, PF/VF reset handling, AER/RAS handling, mailbox and FLR paths, and diagnostics use these definitions indirectly through register access helpers. Direct include-site families in this tree include NBIO 2.3 driver code such as `drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c`, virtualization support such as `drivers/gpu/drm/amd/amdgpu/mxgpu_nv.c`, and SMU/power-management code that includes the same generated register namespace.

The SWDS0 definitions integrate with PCIe downstream-switch/device configuration and diagnostics. The VF0/VF1 definitions integrate with SR-IOV virtual function enumeration, guest-visible PCI capability layout, FLR/reset behavior, interrupt delivery, AER reporting, ATS/ARI negotiation, and hypervisor/PF-mediated policy. Linux PCI core concepts are visible in the field names, but this header is an AMDGPU hardware register map rather than ordinary generic PCI config access code.

## Risks And Edge Cases

- The range has artificial boundaries. It starts mid-`BIF_CFG_DEV0_SWDS0_LINK_CNTL` and ends mid-`BIF_CFG_DEV0_EPF0_VF1_0_PCIE_UNCORR_ERR_STATUS`. Adjacent chunks must be reconciled for whole-register and whole-file conclusions.
- Generated macro drift compiles cleanly when names still exist. A wrong mask or shift can silently program the wrong PCIe capability bit, decode stale status, or corrupt adjacent fields.
- Width mismatches are easy in PCI config space. This chunk mixes 8-bit, 16-bit, and 32-bit logical fields, but all are exposed as untyped C macros.
- PCIe command/status and FLR fields are side-effect sensitive. Incorrect masks around `BUS_MASTER_EN`, `MEM_ACCESS_EN`, error enables, `INT_DIS`, or `INITIATE_FLR` can break enumeration, reset, or guest recovery.
- MSI/MSI-X fields affect interrupt routing. Wrong address/data/control/table/PBA masks can cause lost interrupts, unexpected interrupts, or vectors being exposed before software finishes programming them.
- AER fields are protocol and reliability sensitive. Incorrect status/mask/severity/header-log/TLP-prefix definitions can suppress real errors, misclassify fatal/nonfatal conditions, or produce misleading diagnostics.
- ACS, ATS, ARI, and VC fields are virtualization and isolation sensitive. Wrong masks can alter peer-to-peer routing, translation behavior, function grouping, or traffic-class mapping.
- Link, 8GT/16GT equalization, DLF, and margining fields are hardware-owned or training-sensitive. Treating status bits as ordinary writable configuration can destabilize links or invalidate diagnostics.
- Per-lane generated repetition is vulnerable to mechanical one-off errors. Lanes 0-15 for 8GT equalization, 16GT presets, and margining control/status should remain structurally consistent.
- Full-width address, scratch, log, and payload fields use `0xFFFFFFFF` masks. Reusing those masks against the wrong offset can overwrite unrelated hardware state.

## Test And Validation Signals

Useful validation is mostly build, hardware bring-up, PCIe enumeration, and virtualization coverage:

- Build AMDGPU code paths that include `nbio_2_3_sh_mask.h`; missing or renamed generated macros should fail at compile time in NBIO, SR-IOV, SMU, or PCIe consumers.
- Boot an NBIO 2.3 ASIC and exercise NBIO initialization, PCIe config-space access, doorbell/interrupt setup, HDP/PCIe paths, and link-management paths that rely on the generated register set.
- Enumerate the SWDS0 PCIe capability chain and confirm link, slot, MSI, SSID, vendor-specific, VC, serial-number, AER, secondary PCIe, ACS, DLF, 16GT PHY, and margining capability fields decode correctly.
- Enable SR-IOV and enumerate at least VF0 and VF1, checking standard PCI header fields, capability pointers, PCIe device/link capabilities, MSI/MSI-X visibility, AER capability layout, ATS/ARI visibility, and FLR behavior.
- Run guest VF reset/FLR tests and confirm command/status, link status, MSI/MSI-X state, AER status/logs, ATS/ARI state, and capability layout return to expected hardware defaults.
- Exercise MSI and MSI-X interrupt delivery for PF and VF contexts, including vector programming, vector masking, pending-bit handling, interrupt disable, and reset/re-enable sequences.
- Run PCIe link retraining, suspend/resume, runtime power-management, and error-recovery tests; link training stalls, equalization failures, completion timeouts, AER storms, or bad negotiated width/speed are strong signals of mask/offset drift.
- Use AER or platform error-injection diagnostics, where available, to validate uncorrectable/correctable status, masks, severity bits, first-error pointer, ECRC controls, header logs, and TLP prefix logs.
- In virtualized or peer-to-peer configurations, validate ACS, ATS, ARI, and VC behavior to catch isolation, routing, or translation regressions.
- On platforms exposing PCIe Gen4/16GT diagnostics or margining, verify per-lane equalization presets, parity mismatch reporting, margining ready/software-ready status, and margining control/status payload echo for lanes 0-15.
