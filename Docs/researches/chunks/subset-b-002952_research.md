# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_2_3_sh_mask.h lines 117940-120339

## Scope

This chunk is the final slice of AMDGPU's generated NBIO 2.3 shift/mask header. It contains C preprocessor constants for bit shifts and masks in NBIF/BIF PCI configuration decode space for SR-IOV virtual functions and ends with the file footer.

The range starts mid-register in the `VF27_1` configuration-space block, immediately after the first MSI message-control shift definitions. It then completes the tail of `VF27_1`, contains full `VF28_1`, `VF29_1`, and `VF30_1` PCI/PCIe capability blocks, and finishes with the `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` `BIF_BX_PF1_MM_INDEX`/`MM_DATA` indirect access registers plus `#endif`.

The chunk is declarative. It defines register-field names, bit positions, and bit masks only; it has no functions, structures, executable statements, allocation, locking, or initialization code.

## Purpose

The macros provide symbolic encodings for NBIO 2.3 PCI configuration and BIF indirect MMIO registers so AMDGPU code can decode and compose hardware register values without embedding raw bit constants. The dominant naming pattern is:

- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>__SHIFT`
- `BIF_CFG_DEV0_EPF0_VF<n>_1_<REGISTER>__<FIELD>_MASK`

where `<n>` is `27`, `28`, `29`, or `30` in this range. The companion `nbio_2_3_offset.h` header supplies register addresses, while this file supplies field layouts. The final `BIF_BX_PF1_MM_*` macros define the field layout for an index/data aperture used to address BIF MM registers through `cfgBIF_BX_PF1_MM_INDEX`, `cfgBIF_BX_PF1_MM_DATA`, and `cfgBIF_BX_PF1_MM_INDEX_HI`.

## Address Blocks and Register Coverage

Visible address-block markers in this slice:

- `nbio_nbif0_bif_cfg_dev0_epf0_vf28_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf29_bifcfgdecp`
- `nbio_nbif0_bif_cfg_dev0_epf0_vf30_bifcfgdecp`
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC`

The `VF27_1` block begins before this chunk. This range covers its MSI/MSI-X tail, vendor-specific extended capability, Advanced Error Reporting, ATS, and ARI definitions. `VF28_1`, `VF29_1`, and `VF30_1` are complete within the chunk and repeat the same register families:

- Basic PCI header fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, programming interface, subclass/base class, cache line, latency, header type, BIST, six BARs, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- PCIe capability fields: `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- MSI/MSI-X fields: MSI capability list, message control, low/high address, data, mask, 64-bit data/mask, pending bits, MSI-X capability list, table size/function mask/enable, table BIR/offset, and PBA BIR/offset.
- Vendor-specific PCIe extended capability fields: enhanced capability list header, vendor-specific header, and two 32-bit scratch registers.
- PCIe Advanced Error Reporting fields: enhanced capability list header, uncorrectable error status/mask/severity, correctable error status/mask, AER capability/control, four TLP header log words, and four TLP prefix log words.
- ATS and ARI extended capability fields: ATS enhanced capability list, invalidate queue depth/page-aligned/global-invalidate support, STU, ATC enable, ARI enhanced capability list, ARI capability bits, next function number, function group enables, and function group value.
- PF indirect MM access fields: `BIF_BX_PF1_MM_INDEX__MM_OFFSET`, `BIF_BX_PF1_MM_INDEX__MM_APER`, `BIF_BX_PF1_MM_DATA__MM_DATA`, and `BIF_BX_PF1_MM_INDEX_HI__MM_OFFSET_HI`.

## Important APIs, Types, and Functions

There are no C APIs, type declarations, or functions in this chunk. The externally consumed interface is the macro namespace.

Important macro families:

- `*_COMMAND__*` and `*_STATUS__*` model standard PCI command/status bits such as I/O access, memory access, bus mastering, SERR, interrupt disable, capability-list presence, abort reporting, parity reporting, and PME status.
- `*_BASE_ADDR_*`, `*_ROM_BASE_ADDR__*`, and `*_MSIX_TABLE/PBA__*` expose address/offset fields where low bits encode type, prefetchability, BIR, enablement, or reserved state and must be preserved according to PCI layout.
- `*_PCIE_CAP*`, `*_DEVICE_*`, and `*_LINK_*` cover device/port type, slot implementation, interrupt message number, FLR, payload/read request sizing, relaxed ordering, no-snoop, completion timeout, ASPM, link retrain/disable, negotiated link speed/width, equalization status, and link speed vector fields.
- `*_MSI_*` and `*_MSIX_*` define interrupt capability programming, including MSI enablement, multi-message count, 64-bit MSI addressing, per-vector mask capability, vector mask/pending bits, MSI-X table size, function mask, enable bit, table location, and pending-bit-array location.
- `*_PCIE_UNCORR_ERR_*`, `*_PCIE_CORR_ERR_*`, and `*_PCIE_ADV_ERR_CAP_CNTL__*` define AER status, reporting mask, severity classification, ECRC generation/checking support and enablement, multi-header recording, TLP prefix logging, and completion timeout logging capability.
- `*_PCIE_HDR_LOG*` and `*_PCIE_TLP_PREFIX_LOG*` expose raw 32-bit capture words used when diagnosing PCIe errors.
- `*_PCIE_ATS_*` and `*_PCIE_ARI_*` define address-translation and alternate routing-ID capabilities/controls used when a virtual function participates in IOMMU/ATS and ARI-aware PCIe topologies.
- `BIF_BX_PF1_MM_INDEX*` and `BIF_BX_PF1_MM_DATA*` define the index/data aperture fields for indirect BIF MM access: low offset bits, aperture select bit, high offset bits, and full 32-bit data.

## Control Flow

This header chunk has no runtime control flow. Inclusion is controlled only by the enclosing header guard, which terminates at the `#endif` in this range. At compile time, any translation unit that includes the generated NBIO 2.3 headers receives these constants.

Typical consumer flow is inferred from the macro design:

1. Locate a register through the companion offset header, often via `cfgBIF_CFG_DEV0_EPF0_VF*_1_*` or `cfgBIF_BX_PF1_MM_*` definitions.
2. Read the register through AMDGPU PCI config, MMIO, or indirect register access helpers.
3. Use the `*_MASK` and `*_SHIFT` constants with `REG_GET_FIELD`, `REG_SET_FIELD`, or equivalent bit operations.
4. Write back a composed value when enabling or disabling PCIe features, interrupt delivery, AER controls, ATS/ARI behavior, or indirect BIF MM access.

## State and Persistence Behavior

The header stores no software state and performs no persistence. It describes state held in hardware registers. For the VF configuration blocks, the represented state is per virtual function and can be changed by guest drivers, host PCI/SR-IOV orchestration, PF-mediated setup, reset paths, and PCI core policy.

Some fields are persistent configuration controls until reset or function-level reset, such as `BUS_MASTER_EN`, `MEM_ACCESS_EN`, `IO_ACCESS_EN`, `INTERRUPT_DIS`, MSI/MSI-X enable bits, MSI-X function mask, AER masks/severity controls, ECRC enables, ATS `ATC_ENABLE`, ARI function-group controls, completion timeout controls, and PCIe link-control fields.

Other fields expose hardware status or diagnostic capture, including PCI status bits, device/link status bits, correctable and uncorrectable AER status, AER first-error pointer, TLP header logs, TLP prefix logs, MSI pending bits, and link equalization indicators. These may be read-only, sticky, clear-on-write, or hardware-updated depending on the PCIe register model and the NBIO implementation.

The `BIF_BX_PF1_MM_INDEX`/`MM_DATA` aperture has implicit state in the selected indirect offset. A write to the index/high-index registers selects the target location; reads or writes through `MM_DATA` then operate on that target. Ordering and preservation of `MM_APER`, high offset, and low offset fields matter for correctness.

## Dependencies and Integration Points

This chunk integrates with:

- `nbio_2_3_offset.h`, which maps these field definitions to concrete register addresses and base indices.
- `nbio_2_3_default.h`, which provides reset/default values for related registers, including the final `BIF_BX_PF1_MM_*` aperture.
- AMDGPU register helper macros and generated-register conventions, especially `REG_GET_FIELD`/`REG_SET_FIELD` style accessors that expect matching `__SHIFT` and `_MASK` macro names.
- Linux PCI, PCIe, MSI/MSI-X, SR-IOV, AER, ATS, ARI, and IOMMU subsystems, whose standard capability layouts are mirrored by the generated field names.
- SR-IOV PF/VF management paths. The repeated `VF27_1` through `VF30_1` blocks are per-VF decode windows for high-numbered virtual functions.
- Interrupt setup and teardown paths through MSI/MSI-X address/data, mask, pending, table, and PBA definitions.
- PCIe diagnostics and recovery paths through AER status/mask/severity and TLP log definitions.
- Low-level NBIO/BIF access code through the final PF1 indirect MM index/data aperture.

## Risks and Edge Cases

- The file is generated and highly repetitive. A single generation error in a shift or mask can silently corrupt every consumer that decodes or composes that field.
- The chunk starts in the middle of `VF27_1_MSI_MSG_CNTL`; earlier MSI control shift definitions for `VF27_1` are outside the range. Final reconciliation should avoid treating this chunk as a complete `VF27_1` block.
- `VF28_1`, `VF29_1`, and `VF30_1` should be structurally identical except for the VF number. Copy-generation drift is hard to catch manually because most definitions differ only by that numeric prefix.
- AER field families have very similar names for status, mask, and severity. Mixing them can suppress error reporting, misclassify uncorrectable errors, or inspect/clear the wrong hardware state.
- MSI/MSI-X table/PBA and BAR-like fields include encoded low bits. Consumers must not treat all masked address bits as a plain byte address.
- Link-control fields such as retrain, disable, autonomous width/speed controls, equalization controls, and compliance bits can affect device reachability if written incorrectly.
- ATS and ARI control bits interact with IOMMU and PCIe routing policy. Enabling ATC or ARI behavior without platform support can break DMA translation or function discovery.
- The `BIF_BX_PF1_MM_INDEX` aperture is stateful. Concurrent users or missing serialization around index/data sequences can target the wrong indirect register.
- Literal widths vary between 8-bit, 16-bit, and 32-bit fields while the masks use `L` suffixes. Consumers should avoid implicit truncation or signedness assumptions.

## Test Signals

Useful validation signals for this chunk:

- Compile coverage of AMDGPU code that includes `nbio_2_3_sh_mask.h`; missing, duplicated, or malformed macros should fail normal builds.
- Generated-register consistency checks comparing this `_sh_mask.h` range against `nbio_2_3_offset.h`, `nbio_2_3_default.h`, and the upstream hardware register database.
- Pattern checks across `VF28_1`, `VF29_1`, and `VF30_1` to confirm matching field shifts and masks for the same register families; separately account for the partial `VF27_1` boundary.
- SR-IOV runtime smoke tests with enough VFs enabled to exercise VF27 through VF30: enumerate VFs, bind host/guest drivers, enable memory and bus mastering, and verify config-space decoding.
- MSI/MSI-X tests on high-numbered VFs: program vectors, toggle masks, check pending state, and confirm interrupts are delivered and quiesced as expected.
- PCIe capability inspection using driver debug output or `lspci -vv` to verify payload sizes, link width/speed, FLR, MSI/MSI-X, AER, ATS, and ARI fields match hardware expectations.
- AER injection or observation tests to verify correctable/uncorrectable status, mask, severity, first-error pointer, TLP header logs, and TLP prefix logs decode correctly.
- Reset and lifecycle tests around VF FLR, PF teardown/recreation, and guest detach/attach to confirm status/control fields return to expected defaults.
- Indirect MM aperture tests that write index/high-index/data in controlled sequences and verify `MM_OFFSET`, `MM_APER`, `MM_OFFSET_HI`, and `MM_DATA` select and transfer the expected register contents.
