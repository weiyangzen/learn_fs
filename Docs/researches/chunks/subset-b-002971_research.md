# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 24748-27173

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header slice. It contains C preprocessor constants for bit positions and masks in NBIF/BIF PCI configuration decode space for SR-IOV virtual functions.

The range starts inside the `BIF_CFG_DEV0_EPF0_VF7_0_COMMAND` register, after the first command-field masks and after all command shift definitions. It then covers the rest of the VF7 PCI/PCIe capability block, full VF8 and VF9 PCI/PCIe capability blocks, and the beginning of the VF10 block through the first `DEVICE_CAP2` shift definitions. The next line after this chunk continues `VF10_0_DEVICE_CAP2`, so this range is not a complete VF10 block.

The chunk is declarative. It defines roughly 2,100 `#define` constants over 276 visible register-name prefixes. It has no functions, structs, executable control flow, allocation, locking, initialization, or direct persistence logic.

## Purpose

The macros provide symbolic field layouts for NBIO 4.3.0 PCI configuration-space registers so AMDGPU code and generated register helpers can decode, mask, and compose hardware register values without embedding raw bit constants.

The dominant naming pattern is:

- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_0_<REGISTER>__<FIELD>_MASK`

where `<n>` is mostly `7`, `8`, `9`, or `10` in this slice. The companion `nbio_4_3_0_offset.h` maps these same register names to concrete NBIO configuration-space addresses such as the VF7 window starting around `0xfffe10307000`, while this file describes the field packing inside each addressed register.

## Address Blocks and Register Coverage

Visible address-block markers in this slice:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf8_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf9_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf10_bifcfgdecp`

The `VF7_0` address-block marker and early `COMMAND` definitions are before the chunk. This range begins with `VF7_0_COMMAND` masks for `PAL_SNOOP_EN`, parity response, stepping, SERR, fast back-to-back, and interrupt disable, then covers these VF7 register families:

- PCI header/configuration fields: `STATUS`, revision and class fields, cache line, latency, header type, BIST, BARs 1-6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X fields: capability list headers, MSI message control/address/data/mask/pending registers, MSI-X message control, table location, and PBA location.
- PCIe vendor-specific extended capability fields: capability-list header, vendor-specific header, and two vendor-specific data registers.
- Advanced Error Reporting fields: AER extended capability header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four TLP header log words, and four TLP prefix log words.
- ARI and ready-time reporting fields: ARI enhanced capability list, ARI capability/control, router enhanced capability header, and `RTR_DATA1`/`RTR_DATA2` timing fields.

`VF8_0` and `VF9_0` are complete within this chunk and repeat the same register families as VF7, including basic PCI header fields, PCIe capabilities, MSI/MSI-X, vendor-specific extended capability, AER, ARI, and RTR timing.

`VF10_0` starts at its address-block marker and includes basic PCI header fields through `LINK_STATUS`, plus the initial `DEVICE_CAP2` shifts for completion timeout, ARI forwarding, atomic operation support, CAS128 support, and no-relaxed-ordering peer-to-peer passing. Its `DEVICE_CAP2` remaining shifts, masks, and later capability registers are outside this chunk.

## Important APIs, Types, and Functions

There are no C APIs, type definitions, or functions in this header chunk. The externally consumed interface is the macro namespace.

Important macro families:

- `*_COMMAND__*` and `*_STATUS__*` model standard PCI command/status bits such as memory access, bus mastering, SERR, interrupt disable, capability-list presence, abort reporting, parity reporting, and interrupt status. In this range, VF7 command coverage is partial because earlier masks and shifts are in the previous chunk.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, and adapter/class/header fields describe the virtual function's PCI header layout. BAR-like fields use wide masks such as `0xFFFFFFFFL`, while ROM BAR fields split enable/validation bits from the base-address bits.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*` expose PCIe capability version, device type, slot implementation, payload/read-request sizing, relaxed ordering, no-snoop, FLR, power-management support, ASPM controls, link retrain/disable, common clock, negotiated link speed/width, and link-bandwidth events.
- `*_DEVICE_CAP2` and `*_DEVICE_CNTL2` cover newer PCIe controls and capabilities such as completion timeout values, ARI forwarding, atomic operations, LTR, TPH completer support, 10-bit tags, OBFF, end-to-end TLP prefixes, emergency power reduction, FRS, EETLP blocking, IDO, LTR enable, OBFF enable, emergency power reduction request, and FRS signaling.
- `*_LINK_CAP2`, `*_LINK_CNTL2`, and `*_LINK_STATUS2` define supported link-speed vectors and equalization-related control/status fields, including target speed, enter compliance, selectable de-emphasis, transmit margin, compliance SOS, modified compliance, equalization request, and equalization phase statuses.
- `*_MSI_*` and `*_MSIX_*` define interrupt capability programming, including MSI enablement, multi-message capability/enable, 64-bit address capability, per-vector masking capability, message address/data fields, vector mask/pending bits, MSI-X table size, function mask, enable bit, table BIR/offset, and pending-bit-array BIR/offset.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*` define AER status, reporting masks, severity classification, first-error pointer, ECRC support and enable bits, multiple-header recording, TLP prefix log presence, and completion-timeout prefix/header logging capability.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*` are raw 32-bit capture fields used by PCIe error diagnostics.
- `*_PCIE_VENDOR_SPECIFIC*` exposes the PCIe vendor-specific extended capability header and two 32-bit vendor-defined data registers.
- `*_PCIE_ARI_*` defines Alternate Routing-ID capability/control fields including MFVC and ACS function-group support/enables, next function number, and function-group selection.
- `*_PCIE_RTR_ENH_CAP_LIST`, `*_RTR_DATA1`, and `*_RTR_DATA2` describe ready-time reporting capability headers and timing fields for reset, data-link-up, FLR, D3hot-to-D0, and validity.

## Control Flow

This chunk has no runtime control flow. Inclusion is controlled only by the file-level header guard established at the top of `nbio_4_3_0_sh_mask.h`.

Typical consumer flow is inferred from the generated register convention:

1. A translation unit includes `nbio/nbio_4_3_0_offset.h` and `nbio/nbio_4_3_0_sh_mask.h`.
2. The consumer selects a register address from the offset header, for example a `cfgBIF_CFG_DEV0_EPF0_VF*_0_*` definition.
3. The driver reads the register through AMDGPU MMIO, PCI configuration, or indirect NBIO/BIF access helpers.
4. The value is decoded with the `*_MASK` and `__SHIFT` constants, commonly through `REG_GET_FIELD`-style helpers.
5. If the driver must modify a control register, it composes the new field value with `REG_SET_FIELD`-style helpers and writes the result back.

Local include-level integration confirms the header is pulled into `amdgpu/nbio_v4_3.c` and SMU 13 power-management files. In `nbio_v4_3.c`, adjacent NBIO 4.3.0 masks are used for revision decoding, framebuffer access enablement, doorbell aperture setup, ROM offset extraction, LTR programming, and ASPM programming. The VF-specific macros in this chunk are not directly referenced by ordinary C symbols in the inspected tree snapshot; they are still part of the generated NBIO register ABI available to SR-IOV and diagnostics paths.

## State and Persistence Behavior

The header stores no software state and persists nothing by itself. It describes state held in hardware configuration registers.

Control fields represented here are persistent hardware configuration until reset, function-level reset, PF/VF reinitialization, guest driver action, or host PCI policy changes. Examples include command enable bits, interrupt disable, MSI/MSI-X enable and mask controls, MSI-X function mask, AER masks and severity controls, ECRC enable bits, completion timeout controls, LTR enablement, IDO/OBFF/FRS controls, ARI forwarding, and link-control settings.

Status and diagnostic fields are hardware-updated or sticky according to PCIe rules. Examples include PCI status error bits, device/link status, AER correctable and uncorrectable status, first-error pointer, TLP header logs, TLP prefix logs, MSI pending bits, link equalization phase indicators, link bandwidth status, and RTR valid/timing values. Some status fields may be clear-on-write or write-one-to-clear in hardware even though this generated header does not encode access semantics.

Because these are per-VF configuration blocks, state is scoped to individual SR-IOV virtual functions. VF7, VF8, VF9, and VF10 have separate configuration windows in the offset header and separate field macro namespaces here. Host PF management, guest VF drivers, FLR, PCI reset, and SR-IOV enable/disable sequences can all change the underlying hardware state.

## Dependencies and Integration Points

Primary dependencies and integration points:

- `nbio_4_3_0_offset.h` supplies the register addresses matching these field macro prefixes. For example, the VF7 block begins at `cfgBIF_CFG_DEV0_EPF0_VF7_0_VENDOR_ID` and proceeds through capability offsets for the same register names used in this chunk.
- `amdgpu/nbio_v4_3.c` includes this header and provides the NBIO 4.3 function table (`nbio_v4_3_funcs` and `nbio_v4_3_sriov_funcs`) used by discovery and IP block setup.
- SMU 13 power-management files include the NBIO 4.3.0 offset and mask headers, giving power-management code access to NBIO register field layouts.
- AMDGPU register helper macros such as `REG_GET_FIELD` and `REG_SET_FIELD` depend on the generated `__SHIFT` and `_MASK` naming convention.
- Linux PCI/PCIe concepts are mirrored in the macro names: standard PCI config header, PCIe capability, MSI, MSI-X, AER, ARI, link control/status, completion timeout, LTR, OBFF, FRS, and TLP prefix logging.
- SR-IOV PF/VF orchestration depends on the separate VF configuration windows represented here. These macros describe high-numbered virtual functions in the device 0 endpoint function 0 decode space.
- Interrupt setup and teardown integrate through MSI/MSI-X address, data, mask, pending, table, PBA, and enable/function-mask fields.
- Error handling and RAS diagnostics integrate through AER status/mask/severity and header/prefix log definitions, even though this chunk contains only field constants.

No `nbio_4_3_0_default.h` file was present at the inspected path, so default/reset-value integration for this exact header family is not represented locally the way it is for some other generated NBIO versions.

## Risks and Edge Cases

- The file is generated and highly repetitive. A wrong shift or mask can silently corrupt every consumer that decodes or composes that field.
- The chunk boundaries are partial: VF7 starts mid-`COMMAND` and VF10 ends mid-`DEVICE_CAP2`. Merge/reconciliation must not treat this chunk alone as a complete VF7 or VF10 documentation unit.
- VF8 and VF9 should be structurally identical for same-named registers except for the VF number and offset-window base. Copy-generation drift is hard to spot because most lines differ only by the numeric prefix.
- AER register families have similar field names across status, mask, and severity registers. Using the wrong macro family can clear the wrong status, suppress reporting, or misclassify uncorrectable errors.
- MSI and MSI-X register layouts contain overlapping addresses and encoded low bits in standard PCI capability space. Consumers must not treat all masked address/table/PBA fields as simple byte addresses without preserving BIR and capability-specific bits.
- BAR and ROM BAR fields mix address bits with enable, validation, and type bits. Raw writes that do not preserve low control bits can break PCI resource decoding.
- Link-control and link-control-2 fields can affect link training, target speed, compliance mode, equalization, and bandwidth management. Incorrect writes can degrade performance or make the device unreachable.
- Device capability/control 2 fields interact with platform support for ARI, atomics, LTR, OBFF, 10-bit tags, FRS, and TLP prefixes. Enabling unsupported features can break routing, DMA ordering, or power-management behavior.
- VF configuration state may be concurrently influenced by host PF code, PCI core, virtualization tooling, and guest drivers. Register access needs the same synchronization and ownership assumptions as the surrounding SR-IOV management path.
- Masks use `L` suffixes and cover 8-bit, 16-bit, and 32-bit fields. Consumers should avoid implicit truncation, sign-extension, and width assumptions when using them outside normal AMDGPU register helper macros.

## Test Signals

Useful validation signals for this chunk:

- Compile AMDGPU configurations that include `nbio_4_3_0_sh_mask.h`; malformed macro names, duplicate definitions with different values, or missing generated constants should fail early.
- Generated-register consistency checks comparing this range against the hardware register database and `nbio_4_3_0_offset.h`, including the VF7/VF8/VF9/VF10 window bases and capability offsets.
- Pattern checks across VF8 and VF9 to confirm same-named fields have identical shifts and masks; separately handle partial VF7 and VF10 boundaries.
- SR-IOV smoke tests with enough virtual functions enabled to enumerate VF7 through VF10, bind host/guest drivers, enable memory and bus mastering, and verify PCI config-space access.
- MSI/MSI-X tests on these VFs: program MSI address/data, toggle MSI enable and per-vector mask bits, program MSI-X table/PBA locations, confirm interrupts deliver, mask, unmask, and quiesce correctly.
- PCIe capability inspection with driver debug output or `lspci -vv` to verify payload sizes, max read request, FLR, completion timeout, LTR, OBFF, FRS, ARI, MSI/MSI-X, and link capability/status decode as expected.
- AER injection or observation tests to verify uncorrectable/correctable status bits, masks, severity fields, first-error pointer, ECRC controls, TLP header logs, and TLP prefix logs decode correctly.
- Reset lifecycle tests around VF FLR, PF teardown/recreation, guest detach/attach, and SR-IOV disable/re-enable to confirm status/control fields return to expected defaults.
- Link-management tests that exercise ASPM, target link speed, retrain, equalization status, and bandwidth notification bits without leaving the link in compliance or disabled states.
