# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 26566-28914

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 register-offset header segment for direct `reg...` access to NBIF/BIF PCI configuration-space decode blocks. It contains 2,325 `#define` entries: 1,163 register offset macros and 1,162 matching `_BASE_IDX` macros. Every `_BASE_IDX` in this range is `5`.

The range starts in the tail of the already-open `BIF_CFG_DEV0_EPF0_1` GPUIOV vendor-specific capability block, covering only `GFXSCH_DW7`, `GFXSCH_DW8`, and `UVD1SCH_DW0` through `UVD1SCH_DW8`. It then contains complete address blocks for `BIF_CFG_DEV0_EPF1_1`, `BIF_CFG_DEV0_EPF2_1`, `BIF_CFG_DEV0_EPF3_1`, `BIF_CFG_DEV0_EPF4_1`, and `BIF_CFG_DEV0_EPF5_1`, and starts the `BIF_CFG_DEV0_EPF6_1` block. The chunk ends at `regBIF_CFG_DEV0_EPF6_1_DEVICE_STATUS2`; the rest of EPF6's PCIe capability and extended capability offsets continue in the next chunk.

Although this source tree is under a `ceph-client` mirror, this file is AMDGPU hardware register metadata. It has no direct Ceph or distributed-filesystem logic.

## Purpose

`nbio_7_2_0_offset.h` provides symbolic register-address constants for NBIO 7.2.0 hardware. This chunk maps PCI/PCIe configuration-space registers for device 0 endpoint functions to the SOC15-style register index space used by AMDGPU register-access helpers.

The public surface is preprocessor constants of the form:

- `regBIF_CFG_DEV0_EPF<n>_1_<REGISTER>`: the encoded register index for a PCI config-space register or capability dword.
- `regBIF_CFG_DEV0_EPF<n>_1_<REGISTER>_BASE_IDX`: the register base index, always `5` in this slice.

Several PCI configuration fields intentionally share one offset because the header names subfields within the same dword. Examples include `VENDOR_ID` and `DEVICE_ID` at offset `...0400` for EPF1, `COMMAND` and `STATUS` at `...0401`, class-code bytes at `...0402`, and control/status halves in capability registers such as `DEVICE_CNTL`/`DEVICE_STATUS` and `LINK_CNTL`/`LINK_STATUS`.

## Important Register Families

The opening EPF0 tail covers GPUIOV scheduler dwords in a vendor-specific PCIe capability: graphics scheduler dwords 7-8 and UVD1 scheduler dwords 0-8. The preceding GPUIOV header, mailbox, framebuffer partition, and earlier scheduler offsets are outside this chunk.

`BIF_CFG_DEV0_EPF1_1` is the largest complete block in this range. It starts at address-block base `0xfffe12101000` and register indices beginning at `0x3fff80800400`. It includes conventional PCI header registers, BARs, ROM base, capability pointer, interrupt fields, PM capability, PCIe capability, MSI/MSI-X capability registers, a vendor-specific capability, virtual-channel capability/resource registers, device serial number, Advanced Error Reporting status/mask/severity/log registers, BAR enhanced capability, power-budgeting and Dynamic Power Allocation registers, secondary PCIe link/equalization registers, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, Data Link Feature, 16 GT/s PHY/link/equalization registers, lane margining controls/status for lanes 0-15, VF resize BAR capability/control registers, and a large GPUIOV vendor-specific region.

The EPF1 GPUIOV region includes SR-IOV shadow, interrupt enable/status, reset control, hypervisor/VM mailbox dwords, context/total-framebuffer/offset/region fields, P2P-over-XGMI enable, per-VF framebuffer partition registers for `VF0_FB` through `VF30_FB`, and scheduler dwords for UVD, VCE, GFX, and UVD1 engines. These offsets are integration points for GPU virtualization and mediated resource partitioning.

`BIF_CFG_DEV0_EPF2_1` through `BIF_CFG_DEV0_EPF5_1` are complete slimmer endpoint-function config images. Each begins at a 0x400-register-index stride from the previous function (`0x3fff80800800`, `0x3fff80800c00`, `0x3fff80801000`, and `0x3fff80801400`) and contains 189 offset macros. These blocks cover standard PCI header registers, PM/PCIe/MSI/MSI-X/vendor-specific capability registers, AER status/mask/severity/logs, BAR enhanced capability, power-budgeting, DPA, ACS, PASID, ARI, TPH requester capability/control, and `PCIE_TPH_ST_TABLE_0` through `PCIE_TPH_ST_TABLE_63`. EPF3-EPF5 also include SATA-related `SBRN`, `FLADJ`, and `DBESL_DBESLD` offsets at the same config dword.

`BIF_CFG_DEV0_EPF6_1` starts at address-block base `0xfffe12106000` and register indices beginning at `0x3fff80801800`. This chunk includes only its standard PCI header, PM capability, SATA-related `SBRN`/`FLADJ`/`DBESL_DBESLD`, and the beginning of the PCIe capability through `DEVICE_STATUS2`. Offsets for EPF6 link capability 2 onward, MSI/MSI-X, AER, TPH, and later capability tables are outside this assigned range.

## APIs, Types, And Functions

There are no C functions, types, structs, enums, variables, locks, allocations, or executable statements in this chunk. Its API is the generated macro namespace consumed by C code at compile time.

The macros carry address information only. They do not encode bit positions, masks, reset defaults, access size, read/write permissions, hardware sequencing requirements, clear-on-read behavior, write-one-to-clear semantics, or firmware ownership. Field geometry lives in the sibling `nbio_7_2_0_sh_mask.h` header, which is included alongside this offset header by `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`.

## Control Flow

This header has no runtime control flow. The practical flow is external:

1. AMDGPU code selects a `regBIF_CFG_DEV0_EPF*_1_*` constant for the endpoint function and config-space register it needs.
2. The selected offset and `_BASE_IDX` feed SOC15/NBIO register access helpers or display/NBIO setup paths.
3. Callers combine the offset with masks from `nbio_7_2_0_sh_mask.h` when they need to extract or update fields inside a shared config dword.

The sequence and grouping in this chunk mirror PCI/PCIe configuration-space layout: conventional header first, followed by PM, PCIe, MSI/MSI-X, vendor-specific, AER, and extended capabilities. The generated order is descriptive, not a required programming sequence.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible PCI configuration-space state exposed through NBIO register windows. Persistence and reset behavior are determined by the GPU's NBIO reset domain, PCIe reset, FLR, SR-IOV state, firmware/BIOS initialization, driver suspend/resume restore, and explicit reads or writes performed by AMDGPU code.

The represented hardware state includes identity and class-code registers, command/status enables, BAR and ROM decode state, interrupt routing, PM state, PCIe device/link control and status, MSI/MSI-X configuration, AER status/mask/severity/logs, BAR resizing, power budget and DPA controls, ACS/PASID/ATS/PRI isolation and address-translation controls, multicast and LTR registers, SR-IOV VF layout and VF BAR state, TPH requester steering-table entries, 16 GT/s link/equalization state, lane-margining controls/status, and GPUIOV virtualization resource partitioning.

Because multiple symbolic names can point at the same register index, any read-modify-write against one field can affect sibling fields unless the caller uses the correct shift/mask metadata and preserves unrelated bits.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must remain synchronized with `nbio_7_2_0_sh_mask.h`. There is no `nbio_7_2_0_default.h` in this directory, so reset/default validation for this generation must come from hardware documentation, generated source provenance, or runtime dumps rather than a local default header.

Direct include points found in this tree are:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both the offset and shift/mask headers for NBIO 7.2 support.
- `drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`, which includes the offset header for display resource code.

The semantic dependencies are the PCI and PCIe specifications for conventional endpoint configuration space, PM capability, MSI/MSI-X, PCIe device/link capability, Advanced Error Reporting, Virtual Channel, secondary PCIe/equalization, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, Data Link Feature, 16 GT/s PHY capability, lane margining, and vendor-specific GPUIOV capability layout.

## Risks And Edge Cases

- Chunk boundaries are artificial. This range starts mid-EPF0 GPUIOV block and ends mid-EPF6 block, so final per-file research must merge adjacent chunks before treating either EPF0 or EPF6 as complete.
- Generated offset drift can compile cleanly while sending register accesses to the wrong config-space dword. That is especially risky for AER, ACS, PASID, SR-IOV, MSI/MSI-X, BAR, GPUIOV, and link-control registers.
- `reg...` direct register indices are not interchangeable with `cfg...` high-address PCI config-space offsets used elsewhere in AMD register headers. The prefix identifies the access path.
- Many symbolic names alias the same dword. Callers must use the companion masks and preserve adjacent fields when changing packed registers such as identity, command/status, class code, interrupt fields, device/link control/status, and MSI data/mask registers.
- EPF1 has a much richer capability set than EPF2-EPF5 in this chunk. Code that assumes every endpoint function exposes GPUIOV, SR-IOV, VF resize BAR, lane margining, or 16 GT/s capability offsets may address nonexistent or generation-specific registers on other functions.
- GPUIOV offsets control virtualization-visible resources such as VF framebuffer partitioning, mailbox/context state, interrupt state, reset control, and P2P-over-XGMI enablement. Incorrect writes can break VF isolation, resource accounting, or host/guest coordination.
- AER and status registers may be write-one-to-clear or otherwise side-effectful at the hardware level. The offset header does not signal those semantics.
- All macros in this chunk use base index `5`; if SOC15 base-index tables change or are misapplied, every offset in the slice is affected.

## Test Signals

- Compile AMDGPU with NBIO 7.2 support enabled so consumers of `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h` catch renamed or missing generated symbols.
- Run generated-header consistency checks: every non-`_BASE_IDX` macro in this range should have a matching `_BASE_IDX` macro, every base index should be `5`, and repeated endpoint blocks should maintain the expected 0x400 register-index stride.
- Cross-check offset names against `nbio_7_2_0_sh_mask.h` so each register offset has corresponding field definitions where the register has defined bitfields.
- On NBIO 7.2 hardware, compare decoded register windows with `lspci -vvxxx`, AMDGPU debug register reads, or firmware-provided PCI config dumps for EPF1-EPF6.
- Validate endpoint-function behavior around BAR sizing, MSI/MSI-X programming, AER reporting/clearing, ACS/PASID/ATS enablement, SR-IOV VF layout, TPH steering-table programming, link speed/equalization, lane margining, and suspend/resume restore.
- For virtualization paths, verify GPUIOV mailbox, interrupt, reset, framebuffer partition, VF count/layout, and P2P-over-XGMI state against expected host and guest behavior.
- For this specific chunk, ensure the merge/reconciliation lane records that `BIF_CFG_DEV0_EPF0_1` and `BIF_CFG_DEV0_EPF6_1` are incomplete in this work item while EPF1 through EPF5 are complete in the assigned line range.
