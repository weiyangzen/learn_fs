# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 24224-26565

## Scope

This chunk is a generated AMDGPU NBIO 7.2 register-offset header segment. It contains 2,326 `#define` entries: 1,163 `reg...` address macros and 1,163 matching `reg..._BASE_IDX` macros. There are no C functions, structs, enums, variables, locks, allocations, executable statements, or local algorithms in this range.

The range starts inside the `nbio_pcie0_bifplr6_cfgdecp` address block, after `regBIFPLR6_1_VENDOR_ID`, `DEVICE_ID`, `COMMAND`, and `STATUS` from the previous chunk. It then covers the remainder of `BIFPLR6_1`, three complete root-complex configuration blocks for `BIF_CFG_DEV0_RC1`, `BIF_CFG_DEV1_RC1`, and `BIF_CFG_DEV2_RC1`, and the start of the endpoint-function block `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` through `regBIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_GFXSCH_DW6`.

Although this repository mirror is under a `ceph-client` source tree, this file is AMDGPU hardware register metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_offset.h` is the address half of AMD's generated NBIO 7.2 register interface. Each covered register field has two macros:

- `reg<NAME>` gives the generated register address/offset token used by AMDGPU register-access helpers.
- `reg<NAME>_BASE_IDX` selects the associated SOC15 base-index slot. Every macro in this chunk uses base index `5`.

The chunk maps PCI/PCIe configuration-space windows for NBIO PCIe/root-port and endpoint-function blocks. The names mirror standard PCI configuration headers, PCIe capability structures, extended PCIe capability structures, lane equalization/margining registers, SR-IOV/virtualization controls, and AMD GPU I/O virtualization vendor-specific registers. The header does not define field bit positions; those live in the sibling `nbio_7_2_0_sh_mask.h` header.

## Important Macro Families

The opening `BIFPLR6_1` tail maps a PCIe root-port style configuration block at the `nbio_pcie0_bifplr6_cfgdecp` address block. It includes standard bridge/header fields such as revision/class bytes, cache-line/header/BIST, secondary/subordinate bus configuration, I/O and memory aperture limits, ROM base, interrupt and bridge control registers, PM capability, PCIe device/link/slot/root capabilities, MSI, SSID, MSI mapping, vendor-specific capability, virtual channel resources, device serial number, Advanced Error Reporting, multicast, TLP prefix logs, DPC, ACS, DLF, LTR, secondary PCIe capability, 16 GT/s PHY/link/lane controls, page request, ATS, PASID, SR-IOV, TPH requester, L1 PM, lane margining, ESM lane equalization/margining, and CCIX/ESM metadata.

The `BIF_CFG_DEV0_RC1`, `BIF_CFG_DEV1_RC1`, and `BIF_CFG_DEV2_RC1` sections are complete and structurally repeated root-complex configuration blocks. Each block has 185 address macros plus 185 base-index macros. They cover standard bridge-like PCI config registers, PM and PCIe capabilities, MSI, SSID and MSI mapping, vendor-specific and VC capabilities, serial number, AER, root error status/command/source IDs, multicast, TLP prefix logs, DPC, ACS, DLF, LTR, secondary PCIe capability, 16 GT/s PHY/link/lane equalization, lane margining, ESM lane controls, and CCIX/ESM registers. The only intended difference between these three sections is the device instance and address range: dev0 at `0x3fff7bfd0400...`, dev1 at `0x3fff7bfd0800...`, and dev2 at `0x3fff7bfd0c00...`.

The final `BIF_CFG_DEV0_EPF0_1` section begins the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` endpoint-function address block at base address `0xfffe12100000`. It includes type-0 endpoint identity and BAR registers, PM and PCIe capability registers, MSI/MSI-X, data link feature, AER, BAR enhanced capability, power budgeting, DPA, ACS, ATS, page request, PASID, SR-IOV, TPH requester, LTR, 16 GT/s link/lane controls, lane margining, VF resizable BAR controls, and AMD `GPUIOV` vendor-specific registers. The chunk ends in the middle of the GPUIOV scheduling table after `GFXSCH_DW6`; the next chunk continues with `GFXSCH_DW7`, `GFXSCH_DW8`, and additional scheduler registers.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace:

- `regBIFPLR6_1_*` names PCIe root-port 6 configuration registers.
- `regBIF_CFG_DEV{0,1,2}_RC1_*` names NBIF root-complex configuration registers for devices 0, 1, and 2.
- `regBIF_CFG_DEV0_EPF0_1_*` names endpoint-function 0 registers for NBIF device 0.

Consumers combine these address constants with AMDGPU/SOC15 register helpers and the matching shift/mask macros. Typical include users for this generation are `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` and display resource code under `drivers/gpu/drm/amd/display/dc/resource/dcn301` and `dcn31`. This offset header by itself cannot identify bitfield layout, reset values, write-one-to-clear behavior, or legal programming sequences.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution:

1. AMDGPU code includes `nbio_7_2_0_offset.h`.
2. The code selects a `reg...` macro and its `_BASE_IDX` when reading or writing NBIO 7.2 PCI/PCIe configuration registers.
3. If individual fields are needed, the caller combines this offset macro with companion `*_SHIFT` and `*_MASK` macros from the sibling shift/mask header.
4. Hardware, firmware, the PCI core, or the AMDGPU driver interprets the underlying PCIe configuration state.

The represented hardware flows are external to this header: PCIe enumeration, bus/resource window setup, BAR sizing, bridge/root-port control, link training and equalization, 16 GT/s lane tuning, lane margining, MSI/MSI-X interrupt routing, AER logging, DPC containment, SR-IOV VF setup, PASID/ATS/page-request enablement, TPH, LTR, L1 PM, power budgeting, DPA, and GPU virtualization mailbox/scheduling state.

## State And Persistence Behavior

The header owns no state and persists nothing. It names hardware-visible NBIO 7.2 PCIe configuration registers. Persistence depends on GPU reset domains, PCI function reset or FLR, secondary-bus reset, suspend/resume save-restore, firmware/BIOS initialization, hypervisor virtualization setup, and explicit driver or PCI core writes.

The state represented by this chunk includes bridge apertures and bus numbers, endpoint BARs and ROM base, command/status enables, interrupt configuration, PCIe device/link/slot/root status, error masks/status/logs, lane equalization and margining controls, virtualization controls, VF BAR sizing and framebuffer allocation registers, and GPUIOV mailbox/scheduler dwords. Some registers are read-only capability or status registers; others are writable controls with hardware side effects. The offset macros do not communicate which class a register belongs to.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2 register database and must remain synchronized with companion headers in the same directory, especially `nbio_7_2_0_sh_mask.h` for field extraction/composition. Other generated NBIO 7.2 files may provide default values or related metadata where present.

Direct source integration points include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes this offset header for NBIO 7.2 register access.
- `drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c` and `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`, which include this generated NBIO offset header for display-resource integration on matching ASIC families.
- AMDGPU register helper infrastructure that interprets `reg...` plus `_BASE_IDX` constants for SOC15 register addressing.

Semantic dependencies are the PCI and PCI Express specifications for configuration headers, bridge/root-port capabilities, MSI/MSI-X, AER, DPC, ACS, ATS, page request, PASID, SR-IOV, TPH, LTR, L1 PM, VC, multicast, and lane margining/equalization. The `GPUIOV` vendor-specific registers additionally depend on AMD hardware and virtualization contracts outside this generated header.

## Risks And Edge Cases

- The chunk begins mid-block: the first four `BIFPLR6_1` standard config macros are in the previous chunk. Any final per-file report must merge adjacent chunk context before treating `BIFPLR6_1` as complete.
- The chunk ends mid-block: `BIF_CFG_DEV0_EPF0_1` continues after `GFXSCH_DW6`. GPUIOV scheduling registers are incomplete in this slice.
- Offset drift can compile cleanly while directing register helpers to the wrong PCIe config dword. Symptoms may appear as broken PCI enumeration, bad BAR sizing, lost interrupts, bad AER reporting, link training failures, or virtualization setup failures.
- Many register names intentionally alias the same dword address because PCI config registers pack multiple fields into one 32-bit location, for example revision/class bytes, command/status, device control/status, link control/status, MSI address/data, or lane control/status pairs. Callers must use the shift/mask header and preserve unrelated bits.
- The three `BIF_CFG_DEV*_RC1` blocks are highly repetitive. A single generated-address mismatch in one instance can affect only one root-complex path, making failures topology-dependent.
- SR-IOV, PASID, ATS, ACS, page-request, and GPUIOV registers influence DMA routing, isolation, VF memory exposure, and hypervisor-visible behavior. Incorrect access can become a security or data-isolation issue, not only a device-local bug.
- AER, DPC, root error, and status registers may have write-one-to-clear or latched semantics. An address macro does not imply that generic read-modify-write is safe.
- All entries in this range use `_BASE_IDX 5`; changing the base index or mixing it with a different NBIO generation would target the wrong address aperture.

## Test Signals

- Build AMDGPU with NBIO 7.2 support enabled so include users such as `amdgpu/nbio_v7_2.c` catch missing or renamed macros.
- Run generated-header consistency checks: every `reg...` macro in this chunk should have a matching `reg..._BASE_IDX`, all `_BASE_IDX` values should remain `5`, and repeated `BIF_CFG_DEV0_RC1`, `BIF_CFG_DEV1_RC1`, and `BIF_CFG_DEV2_RC1` register families should remain structurally identical except for expected address strides.
- Cross-check this offset header against `nbio_7_2_0_sh_mask.h` so every decoded field has both an address macro and matching shift/mask definitions.
- On NBIO 7.2 hardware, compare decoded PCI/PCIe config space against `lspci -vvxxx`, PCI core dumps, AMDGPU debugfs register reads, or firmware tables for bridge apertures, BARs, PM state, link status, MSI/MSI-X state, AER/DPC status, SR-IOV state, PASID/ATS/page-request state, and GPUIOV registers.
- Exercise suspend/resume, FLR or GPU reset, secondary bus reset, PCIe retraining, MSI/MSI-X enable/disable, SR-IOV VF creation/destruction, and error-reporting paths to verify callers restore expected configuration and preserve reserved bits.
- For virtualization-facing changes, validate VF framebuffer allocation, VF BAR sizing, HVVM mailbox registers, GPUIOV interrupts, reset control, and scheduler dwords under a hypervisor configuration that actually enables these paths.
