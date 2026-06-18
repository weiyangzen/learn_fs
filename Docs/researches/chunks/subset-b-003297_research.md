# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h lines 92180-94602

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 shift/mask header. It exports C preprocessor constants that name bit positions and masks for PCIe/NBIO configuration-space registers. The register addresses are not in this file; consumers pair these field macros with the matching `regBIFPLR2_1_*` and `regBIFPLR3_1_*` offset macros from the companion NBIO offset header.

The range begins in the `BIFPLR2_1` PCIe root-port image, immediately after the `PCIE_LANE_ERROR_STATUS` comment and shift definition from the previous chunk. It then covers lane equalization, ACS, multicast, L1 PM substates, DPC/RP PIO error logging, ESM/DLF/16 GT/s PHY/margining/CCIX/32 GT/s capability fields for `BIFPLR2_1`. Near the end it switches at `addressBlock: nbio_pcie1_bifplr3_cfgdecp` to the beginning of the `BIFPLR3_1` PCIe configuration image, covering the conventional bridge header, PM/PCIe/MSI/SSID/vendor-specific/VC/device-serial/AER capability headers, and the beginning of `BIFPLR3_1_PCIE_UNCORR_ERR_STATUS`.

## Major Register Groups

- `BIFPLR2_1_PCIE_LANE_ERROR_STATUS` and `BIFPLR2_1_PCIE_LANE_0_EQUALIZATION_CNTL` through lane 15 define 16-lane 8 GT/s-style equalization presets and lane-error status bits. Each lane equalization control has downstream/upstream TX preset and RX preset-hint fields.
- `BIFPLR2_1_PCIE_ACS_*` defines ACS enhanced-capability list metadata plus capability/control bits for source validation, translation blocking, peer-to-peer request/completion redirect, upstream forwarding, egress control, direct translated P2P, I/O request blocking, memory target access controls, and unclaimed request redirect behavior.
- `BIFPLR2_1_PCIE_MC_*` defines multicast capability/control, group count, base-address registers, receive masks, block-all masks, block-untranslated masks, and overlay BAR fields.
- `BIFPLR2_1_PCIE_L1_PM_SUB_*` defines L1 PM substate capability/control fields for PCI-PM L1.1/L1.2, ASPM L1.1/L1.2, link activation, common-mode restore timing, LTR threshold, and power-on timing.
- `BIFPLR2_1_PCIE_DPC_*` and `BIFPLR2_1_PCIE_RP_PIO_*` define Downstream Port Containment capability/control/status/source ID and root-port PIO status, masks, severity, system-error, exception, TLP header logs, and TLP prefix logs.
- `BIFPLR2_1_PCIE_ESM_*` defines an ESM vendor-specific enhanced capability. The most expansive fields are `PCIE_ESM_CAP_1` through `PCIE_ESM_CAP_7`, which enumerate supported ESM data rates in 0.1 GT/s increments from 4.0 GT/s through 28.0 GT/s. The same block includes ESM status/control, CCIX-required/optional ESM capabilities, CCIX ESM status/control, and per-lane 20 GT/s and 25 GT/s TX preset fields.
- `BIFPLR2_1_PCIE_DLF_*` defines data-link feature capability/status bits for local and remote DLF support and exchange enable/valid state.
- `BIFPLR2_1_PCIE_PHY_16GT_*` defines 16 GT/s PHY capability metadata, reserved link cap/control registers, equalization status, local/RTM parity mismatch status, and per-lane DSP/USP 16 GT/s TX presets.
- `BIFPLR2_1_PCIE_MARGINING_*` defines lane margining capability/status plus lane 0-15 margining command/status pairs. Control fields select receiver number, margin type, usage model, and margin payload; status fields report ready/status, payload, and error conditions for each lane.
- `BIFPLR2_1_PCIE_CCIX_*` defines CCIX capability headers, CCIX capability bits, ESM required/optional masks, CCIX ESM control fields such as ESM select, perform equalization, go-to-20/25 GT/s controls, and CCIX optimized/compatible TLP transport controls.
- `BIFPLR2_1_LINK_CAP_32GT`, `LINK_CNTL_32GT`, and `LINK_STATUS_32GT` define PCIe 32 GT/s equalization bypass, no-equalization-needed, modified TS usage, enhanced link behavior, transmitter precoding, and equalization request/status fields.
- `BIFPLR3_1_*` begins another PCIe bridge/root-port configuration image. It covers vendor/device IDs, command/status, revision/class/header/BIST, bus-number and bridge-window registers, ROM BAR, interrupt pins, vendor capability, adapter ID, PM capability/status, PCIe capability, device/link/slot/root cap-control-status registers, PCIe capability 2/link 2/slot 2, MSI message registers, SSID/MSI-map/vendor-specific enhanced capability, virtual channel capability/resources for VC0 and VC1, device serial number, AER enhanced capability metadata, and the first fields of uncorrectable error status.

## Important APIs, Types, And Functions

There are no functions, structs, enums, or runtime APIs in this slice. The exported interface is the generated macro namespace:

- `BIFPLR2_1_<REGISTER>__<FIELD>__SHIFT` and `BIFPLR3_1_<REGISTER>__<FIELD>__SHIFT` provide zero-based bit positions.
- `BIFPLR2_1_<REGISTER>__<FIELD>_MASK` and `BIFPLR3_1_<REGISTER>__<FIELD>_MASK` provide the mask for the field inside the containing register.

This chunk contains 2,165 `#define` entries and 256 register/comment markers. Most logical fields appear as a shift/mask pair. Some groups are partial because the requested line range starts and ends mid-register: the `BIFPLR2_1_PCIE_LANE_ERROR_STATUS` comment and shift are before/at the boundary, while the last visible `BIFPLR3_1_PCIE_UNCORR_ERR_STATUS` masks continue in the following chunk.

## Control Flow

This header has no executable control flow. Runtime behavior appears when AMDGPU code selects NBIO 7.7.0 for a detected ASIC, includes the generated register headers, reads or writes a PCIe/NBIO configuration register through the driver's register access helpers, and uses these masks and shifts to decode or update individual fields.

Typical consumer flow is:

1. Choose the register offset from the matching NBIO 7.7.0 offset header, for example a `regBIFPLR2_1_PCIE_DPC_STATUS` or `regBIFPLR3_1_LINK_STATUS` macro.
2. Read the register using the AMDGPU MMIO or indexed-register path appropriate for NBIO configuration space.
3. Extract a field with `value & *_MASK`, shifted by the matching `*__SHIFT`.
4. For writable controls, preserve unrelated/reserved bits, clear the field mask, insert the shifted new value, and write the register back.

Hardware flows described by this slice include PCIe link equalization at 8/16/20/25/32 GT/s, lane margining, ESM/CCIX link negotiation, ACS isolation policy, multicast address filtering, L1 substate power management, DPC containment, root-port PIO error classification/logging, MSI programming, virtual-channel arbitration, bridge decode-window programming, hotplug/slot reporting, PME/root status, and AER uncorrectable-error reporting.

## State And Persistence

The header is stateless and persists no data. It is a compile-time description of hardware register layout.

The state named by these macros lives in NBIO PCIe configuration registers. Capability fields such as ACS support, multicast support, L1 PM substate support, DPC support, ESM rate support, DLF support, 16/32 GT/s link capability, CCIX capability, PCIe device/link/slot/root capability, MSI capability, VC capability, device serial number, and AER capability are generally hardware- or firmware-defined for the ASIC and port image.

Control fields such as ACS control, multicast enable/group count, L1 PM substate enables, DPC trigger/interrupt controls, DLF exchange enable, lane margining commands, CCIX ESM controls, 32 GT/s controls, PCI command bits, bridge window registers, PM state/PME enable, device/link/slot/root control, MSI enable/message address/data, VC enable/arbitration load, and AER masks/severity are writable hardware state. Their lifetime depends on PCIe reset, GPU reset, suspend/resume, power-gating, and any firmware or driver reinitialization path.

Status/log fields such as lane error status, DPC status/source ID, RP PIO status and logs, ESM status, data-link feature status, 16/32 GT/s equalization status, parity mismatch status, margining status, PCI/secondary/device/link/slot/root status, VC negotiation status, and AER uncorrectable error status are live hardware observations. The macros do not encode reset values, access permissions, read-clear/write-one-to-clear semantics, or reserved-bit write policy.

## Dependencies And Integration Points

These macros depend on the paired NBIO 7.7.0 register-offset definitions and on AMDGPU's generated-register include structure. A field macro such as `BIFPLR2_1_PCIE_DPC_STATUS__DPC_TRIGGER_STATUS_MASK` is only meaningful when paired with the correct `regBIFPLR2_1_PCIE_DPC_STATUS` address for the matching ASIC/IP version. The same applies to `BIFPLR3_1_*` macros, which describe a separate address block under `nbio_pcie1_bifplr3_cfgdecp`.

Integration points include:

- AMDGPU NBIO 7.7.0 ASIC support and register access code that includes `asic_reg/nbio` headers.
- PCIe setup and diagnostics that inspect command/status, bridge windows, class/header, PM, MSI, PCIe device/link/slot/root capability, VC, SSID, and serial-number fields.
- Link-management and validation paths that decode equalization presets/status, negotiated speed/width, retraining, data-link active state, lane error status, margining status, and 16/20/25/32 GT/s capability/control bits.
- RAS/AER and containment paths that use DPC status/control, RP PIO error status/masks/severity/system-error/exception bits, header/prefix logs, AER enhanced capability metadata, and uncorrectable error status fields.
- Security/isolation or peer-to-peer paths that care about ACS controls, multicast translation/blocking fields, direct translated P2P, and CCIX optimized/compatible TLP controls.
- Power-management paths that program L1 PM substates, PM capability/status/control, PME/root status, link clock power management, and power-on/restore timing fields.
- Debug dump tools that need stable field names for `BIFPLR2_1` and `BIFPLR3_1` PCIe configuration-space images.

## Risks

The main risk is silent hardware misprogramming or misdiagnosis if a shift/mask is stale, generated from the wrong hardware description, or paired with an offset from the wrong ASIC/address block. A one-bit error can misclassify AER/DPC errors, corrupt MSI delivery, program the wrong bridge window, alter ACS isolation, force an unintended link retrain/equalization operation, or command lane margining/CCIX ESM behavior on the wrong lane or speed generation.

The range has explicit chunk-boundary hazards. It starts with only the mask half of `BIFPLR2_1_PCIE_LANE_ERROR_STATUS`; the register comment and shift are adjacent to the boundary. It ends after only the first ten `BIFPLR3_1_PCIE_UNCORR_ERR_STATUS` masks; remaining masks for the status fields continue after line 94602. A merged per-file report should reconcile adjacent chunks before calling those groups complete.

The register namespace is highly repetitive. Lane 0-15 groups, 16 GT/s versus 20/25/32 GT/s groups, margining control versus status groups, and `BIFPLR2_1` versus `BIFPLR3_1` address blocks differ only by name fragments but compile as ordinary integer constants. Copy/paste mistakes can decode valid bits from the wrong register or write a control field in the wrong port image.

Many status fields may be latched or write-one-to-clear, and many capability/control registers contain reserved fields. The generated macros do not say which fields are safe to write, which status bits clear on write, which bits are read-only, or whether a read has side effects. Consumers must rely on PCIe specifications, AMD hardware documentation, and existing driver access patterns.

## Test Signals

Useful validation signals are hardware- and integration-facing:

- The AMDGPU tree builds for NBIO 7.7.0 users, proving generated macro names referenced by code resolve.
- Generator/static checks confirm that every complete register group in this chunk has a matching `regBIFPLR2_1_*` or `regBIFPLR3_1_*` offset/base-index definition in the companion offset header.
- Register dumps on matching hardware show plausible `BIFPLR2_1` ACS, MC, L1 PM, DPC, ESM, DLF, 16 GT/s, margining, CCIX, and 32 GT/s capability/status values.
- PCIe enumeration and diagnostics for the `BIFPLR3_1` image report coherent vendor/device/class/header, bridge-window, PM, MSI, PCIe capability, link, slot, root, VC, serial-number, and AER metadata values.
- Link training tests decode expected current speed/width, data-link active/training state, equalization completion/phase bits, 16/20/25/32 GT/s preset/status fields, and lane margining readiness/results.
- Error-injection or RAS tests decode DPC trigger reason/source ID, RP PIO error class/severity/logs, AER uncorrectable status fields, and root/status indications consistently with hardware documentation.
- MSI tests verify message address/data/control programming, interrupt delivery, and mask/pending behavior.
- Suspend/resume, FLR, hot reset, and GPU reset tests verify that writable PCIe/NBIO controls are restored by driver paths rather than assuming this generated header provides defaults.
