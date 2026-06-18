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
