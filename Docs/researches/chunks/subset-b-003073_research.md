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
