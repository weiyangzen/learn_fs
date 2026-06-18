# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 12208-14624

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 register-offset header segment. It contains 2,397 `#define` lines over 2,417 source lines: 1,199 register-name constants and 1,198 matching `_BASE_IDX` constants. There are no C functions, structs, enums, variables, allocations, locks, or executable statements in this range.

The range starts inside the `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp` address block at `regBIF_CFG_DEV1_EPF1_0_DBESL_DBESLD`, after the earlier identity, BAR, interrupt, vendor, and power-management offsets for that endpoint function. It then covers three `DEV2` endpoint-function windows, a complete `BIFPLR0_0` downstream/root-port style window, and the beginning of `BIFPLR1_0`, ending at `regBIFPLR1_0_PCIE_LANE_7_EQUALIZATION_CNTL` without the paired `_BASE_IDX` line or later lane definitions.

Although this repository path sits under a `ceph-client` source mirror, this file is AMDGPU hardware register metadata. It has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_offset.h` provides generated register address constants for NBIO 7.2.0 blocks. Each register macro names a hardware register and maps it to an offset value, while the matching `<register>_BASE_IDX` macro selects the register base table index used by AMDGPU's SOC15/NBIO register access helpers.

This chunk describes PCI/PCIe configuration-space offsets for NBIO endpoint functions and PCIe port/register blocks. Consumers pair these offsets with companion field-layout metadata, such as NBIO 7.2.0 shift/mask headers, and with AMDGPU read/write helpers to enumerate, configure, or diagnose PCIe capabilities without hard-coding raw register numbers at call sites.

## Important Macro Families

The `BIF_CFG_DEV1_EPF1_0` tail covers offset `0x12418` through `0x124fe`. It includes USB DBESL/DBESLD, standard PCIe capability registers, device/link capability and control/status registers, MSI and MSI-X capability offsets, vendor-specific enhanced capability offsets, Advanced Error Reporting offsets, BAR enhanced capability offsets, power budget and Dynamic Power Allocation offsets, ACS/PASID/ARI/TPH requester offsets, a secondary PCIe capability section, per-lane equalization offsets for lanes 0-15, Data Link Feature and Physical Layer 16.0 GT/s capability offsets, parity mismatch status offsets, lane margining control/status offsets for lanes 0-15, Routing ID interpretation reporting offsets, and TPH steering table entries 0-63.

The `BIF_CFG_DEV2_EPF0_0` block covers a larger endpoint-function window from `0x14000` through `0x14121`. It includes conventional PCI endpoint configuration offsets, BARs 1-6, CardBus CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant/max latency, vendor and power-management capability offsets, PCIe capability offsets, MSI/MSI-X offsets, vendor-specific and AER offsets, BAR/power/DPA/ACS/PASID/ARI/TPH offsets, secondary PCIe capability offsets, lane equalization, Data Link Feature, 16.0 GT/s PHY/link/parity offsets, and lane margining through lane 15. Unlike the EPF1/EPF2 blocks later in this chunk, this EPF0 range includes the 16 GT/s and lane-margining families.

The `BIF_CFG_DEV2_EPF1_0` and `BIF_CFG_DEV2_EPF2_0` blocks repeat the endpoint-function layout at `0x14400`-`0x144fe` and `0x14800`-`0x148fe`. They include conventional endpoint configuration, PCIe capabilities, MSI/MSI-X, vendor-specific and AER registers, BAR/power/DPA, ACS/PASID/ARI/TPH requester capability offsets, secondary capability and per-lane equalization offsets, Data Link Feature, Routing ID interpretation reporting, and TPH steering table entries 0-63. In this chunk these two function windows do not include the later 16 GT/s parity and lane-margining families seen in `DEV2_EPF0_0`.

The `BIFPLR0_0` block runs from `0x400000` through `0x400132`. It describes a PCIe port/root-port style configuration window: conventional bridge configuration, bus-number and I/O/memory/prefetchable windows, interrupt and bridge-control registers, vendor and PM capabilities, PCIe device/link/slot/root capability and control/status registers, MSI and subsystem/MSI-map capabilities, vendor-specific and VC capabilities, device serial number, AER/root error reporting and TLP prefix logs, secondary PCIe capability, per-lane equalization, ACS, Data Link Feature, 16 GT/s PHY/link/parity/equalization, lane margining, CCIX capability/header/status/control, 20 GT/s and 25 GT/s ESM equalization offsets, and CCIX transport capability/control.

The `BIFPLR1_0` block begins at `0x400400` and is partial in this chunk. It covers the same initial bridge, PM, PCIe, slot/root, MSI, SSID/MSI-map, vendor-specific, VC, device serial number, AER, secondary capability, and lane equalization families through lane 7. The line range ends before the `_BASE_IDX` for lane 7 and before lanes 8-15 or any later BIFPLR1 capabilities.

## APIs, Types, And Functions

There are no callable APIs or C data types in this chunk. The public interface is the preprocessor macro namespace:

- `regBIF_CFG_DEV*_EPF*_0_*` macros for NBIF endpoint-function PCI/PCIe configuration registers.
- `regBIFPLR*_0_*` macros for PCIe port/root-port configuration registers.
- `*_BASE_IDX` macros, almost all equal to `5` in this range, selecting the AMDGPU register base index.

The constants encode register offsets only. They do not encode field masks, access widths, reset values, read/write permissions, write-one-to-clear behavior, ownership by firmware versus driver, or programming order. Callers must pair them with the correct shift/mask/default metadata and the correct AMDGPU access path.

## Control Flow

This header has no local runtime control flow. Runtime use is external:

1. ASIC-specific AMDGPU code selects the NBIO 7.2 path and includes this generated header.
2. Driver code chooses a register macro for the relevant endpoint function or PCIe port block.
3. The selected offset and base index are passed through AMDGPU register helpers or PCI/NBIO config-space accessors.
4. Field values are decoded or composed with companion shift/mask macros, and hardware-visible PCIe configuration, link, interrupt, error-reporting, or diagnostic state is read or updated.

The names imply hardware flows for PCIe enumeration, endpoint and port capability discovery, MSI/MSI-X programming, AER logging and masking, BAR and bridge window decode, ACS/PASID/ARI/TPH feature exposure, Data Link Feature exchange, high-speed link equalization, lane margining, CCIX/ESM link capability, and Routing ID interpretation reporting. Sequencing for those flows is not implemented here.

## State And Persistence Behavior

The header owns no state, performs no I/O by itself, and persists nothing. It names hardware registers whose contents are owned by NBIO/PCIe hardware, platform firmware, the Linux PCI core, and AMDGPU initialization, reset, interrupt, RAS, or diagnostic paths.

Represented state includes PCI identity and class-code fields, command/status bits, BAR and ROM decode state, interrupt routing fields, PM and PCIe capability state, MSI/MSI-X address/data/mask/pending state, AER status/mask/severity and log state, BAR enhanced capability and power-budget policy, DPA state, ACS/PASID/ARI/TPH controls, per-lane equalization settings, DLF status/control, 16 GT/s link and parity status, lane-margining command/status payloads, root-port bridge windows, slot/root control/status, VC resource state, CCIX/ESM state, and TPH steering tables.

Persistence across GPU reset, function-level reset, secondary bus reset, PCIe hot reset, runtime power management, suspend/resume, BACO, or firmware reinitialization is not specified by these macros. Any writable policy state represented here must be restored by the owning driver or firmware path according to the hardware programming guide.

## Dependencies And Integration Points

Direct include sites found in this tree include `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`, and `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`. Those consumers depend on symbol stability in this generated header.

The main companion dependency is the NBIO 7.2.0 shift/mask metadata that gives bit positions and masks for the registers named here. The offsets are also tied to AMDGPU SOC15/NBIO register base tables: using the wrong `_BASE_IDX`, or mixing a `BIF_CFG_DEV2_EPF1_0` offset with a different endpoint/function access path, can produce plausible but wrong hardware accesses.

Integration points include AMDGPU NBIO initialization, PCIe configuration and link management, Linux PCI enumeration and capability concepts, display-resource code that needs NBIO offsets, MSI/MSI-X interrupt routing, AER/RAS error collection, ACS/PASID/ARI/IOMMU-related feature handling, TPH requester steering, high-speed link equalization and lane margining diagnostics, and CCIX/ESM capability handling for the port blocks.

## Risks And Edge Cases

- Generated offset drift can compile cleanly while directing a read or write to the wrong hardware register. In this chunk that could affect endpoint enumeration, BAR decode, MSI/MSI-X delivery, AER status, link training, ACS isolation, PASID/ARI exposure, TPH steering, or port bridge windows.
- The chunk starts mid-register-family for `BIF_CFG_DEV1_EPF1_0`: `SBRN` and `FLADJ` at the same offset are immediately before the range, while `DBESL_DBESLD` is inside it. Whole-file reconciliation must include the previous chunk for the full register group.
- The chunk ends mid-register-family for `BIFPLR1_0`: `regBIFPLR1_0_PCIE_LANE_7_EQUALIZATION_CNTL` is present at line 14624, but its `_BASE_IDX` and the lane 8-15 equalization offsets are outside this range.
- Repeated endpoint-function blocks are easy to confuse. `DEV2_EPF0_0`, `DEV2_EPF1_0`, and `DEV2_EPF2_0` share many names but have different offset windows and not identical coverage in this chunk.
- Several names alias the same offset because PCI config dwords contain multiple logical fields, such as command/status, device control/status, link control/status, MSI data variants, DPA status/control, and per-lane controls packed two or four lanes per dword. Callers must use matching masks and preserve unrelated fields.
- Status and error registers such as PCI status, AER status, root error status, parity mismatch status, lane margining status, and MSI pending may have sticky or write-one-to-clear semantics not visible in this offset header.
- Link equalization, lane margining, target speed, CCIX/ESM, DPA, ACS, PASID, ARI, and TPH controls can affect traffic routing, link stability, isolation, or translation/interrupt behavior. Writes require hardware-specific sequencing and reserved-bit preservation.
- `BIFPLR0_0` and `BIFPLR1_0` look structurally similar but are distinct port instances. Cross-port macro mixups can make diagnostics point at the wrong physical link or configure the wrong bridge aperture.

## Test Signals

- Build AMDGPU configurations that include NBIO 7.2.0 support and the DC resource files that include this header. Compile coverage catches removed, renamed, or malformed generated symbols.
- Run generated-header consistency checks for this line range: each register macro should have a paired `_BASE_IDX` inside the range except the intentional boundary at line 14624, all `_BASE_IDX` values here should remain `5`, and repeated endpoint/port families should maintain expected offset spacing.
- Cross-check register names in this chunk against the NBIO 7.2.0 shift/mask headers so every offset used by driver code has matching field definitions and no endpoint/root-port family is accidentally paired with another block's fields.
- Validate endpoint enumeration on NBIO 7.2 hardware by comparing decoded vendor/device IDs, class codes, BARs, capability pointers, MSI/MSI-X state, and PCIe capability registers with Linux PCI core views.
- Exercise interrupt paths using MSI and MSI-X, including mask/pending handling where available, to catch offset or aliasing errors in the endpoint-function windows.
- Exercise PCIe AER and RAS-style diagnostics: uncorrectable/correctable status, masks, severity, header logs, TLP prefix logs, root error command/status, and source IDs should decode consistently with hardware events.
- Exercise link retrain/equalization and high-speed link diagnostics on affected ports, including 16 GT/s status, per-lane equalization, lane error status, and lane margining control/status.
- Validate suspend/resume, runtime power management, GPU reset, FLR, and secondary-bus reset paths to confirm writable policy fields are restored and no code assumes persistence that this header does not guarantee.

## Chunk Boundary Notes

The previous chunk is required for the beginning of `BIF_CFG_DEV1_EPF1_0`, including the register aliases at offset `0x12418` that precede `DBESL_DBESLD`. The following chunk is required to complete `BIFPLR1_0_PCIE_LANE_7_EQUALIZATION_CNTL`, lanes 8-15, and the later `BIFPLR1_0` capability families. The final per-file report should reconcile these boundaries rather than treating them as missing source definitions.
