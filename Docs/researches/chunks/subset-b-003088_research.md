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
