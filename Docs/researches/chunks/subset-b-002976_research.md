# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_sh_mask.h lines 36824-39244

## Scope

This chunk is a generated AMDGPU NBIO 4.3.0 shift/mask header slice. It covers PCI/PCIe configuration-space field definitions for `BIF_CFG_DEV0_EPF0` SR-IOV virtual functions `VF0` through `VF3`.

The range starts inside the `VF0_DEVICE_CAP2` register: line 36823, just before the requested range, defines the `CPL_TIMEOUT_RANGE_SUPPORTED` shift, while line 36824 begins at `CPL_TIMEOUT_DIS_SUPPORTED`. It then completes the remainder of the `VF0` PCIe capability, MSI/MSI-X, vendor-specific, AER, TLP log, and ARI field families. `VF1` and `VF2` are complete logical VF blocks in this range. `VF3` begins at its PCI header fields and continues through the first masks of `PCIE_UNCORR_ERR_SEVERITY`; the rest of `VF3_PCIE_UNCORR_ERR_SEVERITY` and later `VF3` AER/ARI fields are outside this chunk.

The chunk is declarative only. It contains `#define` constants for field shifts and masks. It has no functions, structs, enums, runtime branches, allocation, locking, I/O calls, or initialization code.

## Purpose

The macros give symbolic names to NBIO 4.3.0 PCIe configuration register fields so AMDGPU and related generated-register helpers can read, decode, compose, and write hardware register values without open-coded bit positions.

The dominant naming pattern is:

- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_<REGISTER>__<FIELD>_MASK`

where `<n>` is `0`, `1`, `2`, or `3` in this chunk. The companion offset header maps register names to addresses; this `_sh_mask.h` file maps each register's fields to bit positions and bit masks.

## Register Coverage

The visible register-comment markers show 263 register blocks and 2149 macro definitions in the requested line range. Coverage is source-tree aligned to the requested header slice:

- Partial `VF0` PCIe capability tail: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- `VF0` MSI/MSI-X: MSI capability list, message control, low/high message address, data, extended data, mask, 64-bit data/mask variants, pending bits, MSI-X capability list, message control, table, and PBA location.
- `VF0` vendor-specific and AER tail: vendor-specific enhanced capability/header/scratch fields, AER enhanced capability list, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four header-log words, four TLP-prefix-log words, and ARI enhanced capability/capability/control.
- Complete `VF1` and `VF2` PCI configuration blocks: vendor/device ID, command/status, revision/interface/class fields, cache line/latency/header/BIST, BAR1-BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, max latency, PCIe capability, device/link capability/control/status, second-generation PCIe capability/control/status, MSI/MSI-X, vendor-specific capability, AER, TLP logs, and ARI.
- Partial `VF3` block: basic PCI header fields, BARs, PCIe capability, device/link controls and status, MSI/MSI-X, vendor-specific capability, AER enhanced capability list, uncorrectable error status, uncorrectable error mask, and the shift fields plus first three masks of uncorrectable error severity.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or functions in this chunk. The public interface is the generated macro namespace.

Important macro families:

- `*_COMMAND__*` and `*_STATUS__*` describe standard PCI control and status fields such as I/O access, memory access, bus mastering, SERR, interrupt disable, capability-list presence, abort status, parity error, and detected parity.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, `*_MSIX_TABLE__*`, and `*_MSIX_PBA__*` expose address-like fields where low bits encode memory type, prefetchability, enablement, BIR, or offset metadata.
- `*_PCIE_CAP*`, `*_DEVICE_CAP*`, `*_DEVICE_CNTL*`, and `*_DEVICE_STATUS*` cover PCIe capability version/type, FLR, error reporting, payload size, read request size, relaxed ordering, no-snoop, completion timeout, atomic operations, ten-bit tags, OBFF, emergency power reduction, and TLP prefix support.
- `*_LINK_CAP*`, `*_LINK_CNTL*`, and `*_LINK_STATUS*` describe supported/current link speeds, link width, ASPM/L1 behavior, link disable/retrain, common clocking, clock power management, bandwidth interrupts/status, equalization status, crosslink state, DRS support, and compliance controls.
- `*_MSI_*` and `*_MSIX_*` define interrupt capability fields, including MSI enablement, multi-message capability/count, 64-bit MSI addressing, per-vector masking capability, message data, masks, pending bits, MSI-X function mask/enable, table size, table BIR/offset, and PBA BIR/offset.
- `*_PCIE_VENDOR_SPECIFIC*` exposes PCIe vendor-specific extended capability headers and two 32-bit scratch registers.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*` define AER status, reporting masks, severity classification, first-error pointer, ECRC generation/checking support and enables, multi-header recording, TLP prefix log presence, and completion-timeout log capability.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*` expose raw diagnostic capture words for PCIe error analysis.
- `*_PCIE_ARI_*` defines Alternate Routing-ID capability and control fields: function-group capabilities, next function number, function-group enables, and function group value.

## Control Flow

This header chunk has no runtime control flow. Inclusion is governed by the enclosing header guard outside this slice, and all definitions become compile-time constants for translation units that include the generated NBIO 4.3.0 register headers.

Typical consumer flow is inferred from AMDGPU generated-register conventions:

1. Select a register address from the matching NBIO 4.3.0 offset header.
2. Read the register through PCI configuration, MMIO, or AMDGPU register access helpers.
3. Decode fields with `*_MASK` and `*_SHIFT`, often through `REG_GET_FIELD`-style helpers.
4. Compose writes with the matching field constants, often through `REG_SET_FIELD`-style helpers, when programming PCIe controls, interrupt delivery, AER policy, ARI behavior, or VF config-space state.

## State and Persistence Behavior

The file stores no software state and performs no persistence. It describes state held by hardware registers in NBIO/BIF PCI configuration decode space.

The represented state is per virtual function. Some fields model durable configuration until reset, function-level reset, guest reprogramming, or PF-mediated SR-IOV teardown: command bits, bus mastering, memory access, interrupt disable, payload/read-request sizing, completion-timeout controls, MSI/MSI-X enables and masks, MSI-X function mask, AER masks/severity settings, ECRC enablement, link-control fields, and ARI function-group controls.

Other fields are status or diagnostic capture: device/link status, link training/equalization indicators, MSI pending bits, correctable and uncorrectable AER status, first-error pointer, TLP header logs, and TLP prefix logs. Depending on the PCIe register model and NBIO implementation, these may be read-only, hardware-updated, sticky, write-one-to-clear, or reset by VF/PF lifecycle events.

Because this is SR-IOV VF config-space layout, practical ownership can be split between guest VF drivers, the host PF driver, firmware/hardware reset logic, and Linux PCI core policy. Consumers must preserve reserved bits and avoid treating status-like fields as normal writable storage.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_4_3_0_offset.h`, which provides concrete register offsets for the field names defined here.
- `nbio_4_3_0_default.h`, where generated reset/default values for related NBIO registers are normally stored.
- AMDGPU register helpers and generated-register naming conventions that expect matching `__SHIFT` and `_MASK` symbols.
- Linux PCI and PCIe subsystem concepts mirrored by the generated names: config header, PCIe capability, MSI, MSI-X, SR-IOV VFs, AER, ARI, link training, and power-management policy.
- SR-IOV PF/VF management paths that expose or virtualize these config-space fields for `VF0` through `VF3`.
- Interrupt setup and teardown paths that program MSI/MSI-X address/data/mask/pending/table/PBA state.
- PCIe diagnostics and recovery paths that inspect AER status, masks, severity, header logs, prefix logs, and link status after errors.

## Risks and Edge Cases

- The file is generated and highly repetitive. A wrong shift or mask can compile cleanly while causing incorrect hardware programming or misleading diagnostics.
- This chunk has two partial boundaries. It omits the first `VF0_DEVICE_CAP2` shift at line 36823 and stops in the middle of `VF3_PCIE_UNCORR_ERR_SEVERITY`; merge/reconciliation should not treat either boundary as a complete register family.
- `VF1` and `VF2` should be structurally identical except for the VF number. Copy-generation drift is hard to detect manually because most lines differ only by prefix.
- Status, mask, and severity AER registers use very similar names. Mixing them can clear, suppress, or misclassify PCIe errors.
- BAR, ROM BAR, MSI-X table, and MSI-X PBA fields include encoded low bits. Consumers must not treat every masked value as a plain byte address.
- Link-control and link-control-2 fields can disable links, force retraining, enter compliance modes, or alter autonomous speed/width behavior. Incorrect writes can make a function unreachable or unstable.
- MSI/MSI-X fields interact with Linux interrupt allocation and guest/host VF ownership. Stale mask, pending, or message data handling can lose interrupts or deliver them to the wrong vector.
- ARI fields affect PCIe routing and function discovery. Enabling function-group behavior without platform support can break VF enumeration or isolation assumptions.
- Masks use `L`-suffixed integer literals over 8-bit, 16-bit, and 32-bit fields. Callers should avoid signedness and truncation assumptions when composing values.
- Reserved fields such as `DEVICE_STATUS2__RESERVED` are named but should still be preserved according to the hardware specification.

## Test Signals

Useful validation signals for this chunk:

- Build coverage for AMDGPU code that includes `nbio_4_3_0_sh_mask.h`; malformed macro names or duplicate definitions should fail compilation.
- Generated-register consistency checks comparing this range with `nbio_4_3_0_offset.h`, `nbio_4_3_0_default.h`, and the upstream hardware register database.
- Pattern checks across complete `VF1` and `VF2` blocks to confirm identical field shifts and masks for the same register families; handle the partial `VF0` and `VF3` boundaries separately.
- SR-IOV runtime smoke tests with at least four enabled VFs: enumerate `VF0` through `VF3`, bind host/guest drivers, enable memory access and bus mastering, and verify config-space decoding.
- MSI/MSI-X tests for low-numbered VFs: allocate vectors, program message address/data, toggle vector/function masks, inspect pending state, and confirm interrupt delivery and quiescence.
- PCIe capability inspection through driver debug output or `lspci -vv` to validate payload size, read request size, FLR, link speed/width, MSI/MSI-X, AER, and ARI fields against hardware expectations.
- AER injection or observation tests to verify correctable and uncorrectable status, mask, severity, first-error pointer, TLP header logs, and TLP prefix logs decode correctly.
- Reset and lifecycle tests around VF FLR, PF driver reload, SR-IOV disable/re-enable, and guest detach/attach to confirm status/control fields return to expected defaults.
