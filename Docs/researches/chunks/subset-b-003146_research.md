# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 1-2409

## Purpose

This chunk is the opening slice of the generated AMD NBIO 7.2.0 register offset header. It provides preprocessor constants for PCI/PCIe configuration-space offsets in NBIO root-complex, endpoint-function, and PCIe root-port decode blocks. The file does not perform register I/O by itself; it names byte offsets that AMDGPU and display code combine with the matching NBIO 7.2.0 shift/mask header and AMDGPU register access helpers.

The covered range starts with the license and `_nbio_7_2_0_OFFSET_HEADER` include guard, then defines:

- `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp` root-complex config blocks.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` through `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp` endpoint-function blocks.
- The start of `nbio_pcie0_bifplr0_cfgdecp`, a root-port block, through its full PCIe/CCIX/ESM/DPC/RP PIO coverage.
- The start of `nbio_pcie0_bifplr1_cfgdecp`, ending at `cfgBIFPLR1_SLOT_STATUS2` because the requested chunk ends mid-block at line 2409.

## Public Surface In This Chunk

The exported surface is entirely `#define` macros. Each macro maps a symbolic register name to a byte offset within an address block whose generated comment gives `base address: 0x0`. There are no C functions, structs, enums, or inline helpers in this chunk.

The naming scheme encodes the config-space target:

- `cfgBIF_CFG_DEV0_RC_*` and `cfgBIF_CFG_DEV1_RC_*` are root-complex register offsets for two device views. They include PCI header fields, bridge windows, PM capability, PCIe capability, MSI/MSI-map/SSID, vendor-specific extended capability, VC resources, device serial number, AER, secondary PCIe equalization, ACS, data link feature, 16 GT/s PHY fields, and lane margining.
- `cfgBIF_CFG_DEV0_EPF0_*` and `cfgBIF_CFG_DEV0_EPF1_*` are rich endpoint-function templates. They include standard endpoint header/BAR/MSI/MSI-X registers, PCIe capabilities, AER, resizable BAR, power budget, dynamic power allocation, secondary PCIe, ACS, ATS, PRI, PASID, multicast, LTR, ARI, SR-IOV, TPH requester, 16 GT/s PHY, lane margining, VF resizable BAR, and AMD GPU IOV vendor-specific registers.
- `cfgBIF_CFG_DEV0_EPF2_*` through `cfgBIF_CFG_DEV0_EPF6_*` are leaner endpoint-function templates. They keep endpoint header/MSI/MSI-X, USB-like `SBRN`/`FLADJ`/`DBESL_DBESLD` offsets, PCIe capability, AER, BAR capability/control, power budget, DPA, ACS, PASID, ARI, TPH requester, and a 64-entry TPH steering tag table.
- `cfgBIFPLR0_*` is a root-port style PCIe block. It covers standard bridge registers, PM/PCIe/MSI/SSID/MSI-map, vendor-specific capability, VC resources, serial number, AER/root error, secondary PCIe equalization, ACS, multicast, L1 PM substates, DPC, RP PIO, ESM, data link feature, 16 GT/s PHY, margining, CCIX, and 20/25 GT/s ESM equalization offsets.
- `cfgBIFPLR1_*` begins the next root-port block and, in this chunk, reaches only the standard bridge header and early PCIe capability fields through slot status 2.

## Important Register Families

The root-complex blocks (`DEV0_RC` and `DEV1_RC`) mirror PCI bridge/root-port configuration space. They define vendor/device IDs, command/status, class-code bytes, BARs, bus numbering, IO/memory/prefetchable windows, interrupt/bridge control, PM capability, PCIe device/link/slot/root capability and control registers, MSI registers, SSID and MSI-map, vendor-specific capability, VC capability/resource registers, device serial number, AER status/mask/severity/log/root-error/source-ID registers, TLP prefix logs, secondary PCIe link control and per-lane equalization, ACS, data link feature, 16 GT/s PHY and parity mismatch status, and lane margining control/status pairs for lanes 0-15.

`EPF0` and `EPF1` are the most complete endpoint blocks. Their standard endpoint area includes six BARs, ROM BAR, capability pointer, MSI and MSI-X tables/PBA, and common PCIe capability offsets. They also include virtualization and advanced PCIe features: ATS, PRI, PASID, multicast, LTR, ARI, SR-IOV VF sizing and BAR offsets, TPH requester control, 16 GT/s PHY, lane margining, and VF resizable BAR controls. Their AMD GPU IOV vendor-specific range at `0x0500` includes SR-IOV shadow, interrupt enable/status, reset control, hypervisor/VM mailbox doublewords, context, total framebuffer, offsets, region, P2P-over-XGMI enable, VF0 through VF30 framebuffer windows, and scheduler register windows for UVD, VCE, GFX, and UVD1.

`EPF2` through `EPF6` share a narrower repeated template. They include endpoint identity/header/BAR/MSI/MSI-X and selected advanced capabilities, but omit the large GPU IOV vendor-specific and SR-IOV/VF BAR regions present in `EPF0`/`EPF1`. Each exposes a 64-entry `PCIE_TPH_ST_TABLE_*` range from `0x037c` through `0x03fa`, suggesting per-function steering-tag table entries for TPH requester operation.

`BIFPLR0` is a root-port block rather than a function endpoint. Its offsets cover bridge windows, root control/status, MSI, VC, AER, root error reporting, ACS, multicast, L1 PM substates, DPC containment, RP PIO status/mask/severity/sys-error/exception/log registers, ESM capability/status/control/capability registers, data link feature, 16 GT/s PHY, margining, CCIX capability/control/status, and per-lane ESM equalization controls for 20 GT/s and 25 GT/s operation. `BIFPLR1` starts a similar block but the requested lines stop before its AER and extended root-port regions.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A translation unit includes `nbio_7_2_0_offset.h`.
2. Caller code selects an offset macro for the target NBIO address block.
3. Caller code reads or writes the hardware register through an AMDGPU MMIO/indirect register helper or PCIe config-space path.
4. Field extraction or composition is performed with the matching `nbio_7_2_0_sh_mask.h` macros.

The header owns no state and persists nothing. Persistent behavior belongs to the GPU hardware registers named by these offsets. Several registers represented here can have hardware side effects when accessed by consumers: AER and correctable/uncorrectable error status, root error status, DPC status, RP PIO logs, MSI/MSI-X routing, bridge windows, SR-IOV/VF BAR state, ACS isolation controls, ATS/PRI/PASID enablement, TPH steering tables, link retraining/equalization controls, lane margining, data link feature state, and GPU IOV reset/mailbox/framebuffer partition registers.

## Dependencies And Integration Points

This header is paired with `nbio_7_2_0_sh_mask.h`, which supplies bit positions and masks for fields at the offsets defined here. There is no sibling `nbio_7_2_0_default.h` in this source tree, so reset/default validation for this generation depends on hardware documentation, dumps, or other generated assets outside the observed NBIO directory.

Direct includes in the source tree include:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which also includes `nbio_7_2_0_sh_mask.h` and implements NBIO 7.2 callbacks for HDP flush offsets, PCIe index/data offsets, doorbell aperture ranges, interrupt handler doorbells, memory-controller access, clock gating, light sleep, register remapping, and initialization.
- `drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c`.
- `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c`.

`amdgpu_discovery.c` selects `nbio_v7_2_funcs` for devices that advertise the matching IP version, so these constants sit under the runtime IP-discovery path rather than being globally valid for every AMDGPU device. Display resource code includes the offset header to reach NBIO/PCIe-related registers needed by DCN 3.0.1 and DCN 3.1 resource handling.

The semantic dependencies are PCI and PCIe configuration-space layouts and extended capability definitions: PM, MSI/MSI-X, PCIe device/link/slot/root capabilities, VC, AER, ACS, ATS, PRI, PASID, multicast, LTR, ARI, SR-IOV, TPH, data link feature, physical-layer 16 GT/s capability, lane margining, DPC, RP PIO, ESM, and CCIX. The AMD GPU IOV vendor-specific offsets additionally depend on AMD's SR-IOV/virtualization contract for framebuffer partitioning, scheduling windows, reset, mailbox, and P2P-over-XGMI controls.

## Risks And Maintenance Notes

- The file is generated-style hardware ABI data. A wrong offset can make otherwise correct driver code read or write the wrong config register with little compile-time warning.
- The requested chunk ends in the middle of `BIFPLR1`; adjacent chunks are required for the complete BIFPLR1 root-port analysis.
- Offset values are byte-addressed and include 8-bit, 16-bit, and 32-bit config-space registers. Callers must use access widths that match the register definition; the header name alone does not enforce width.
- Some offsets intentionally alias depending on mode or capability layout. Examples in this chunk include MSI address/data/mask/pending locations where 32-bit and 64-bit MSI layouts share or reinterpret nearby offsets.
- `EPF0`/`EPF1` have large GPU IOV vendor-specific windows absent from `EPF2`-`EPF6`. Treating all endpoint functions as layout-identical would corrupt virtualization or capability handling.
- Root-complex/root-port control registers for bridge windows, ACS, DPC, AER, L1 PM substates, retraining, equalization, margining, and CCIX can affect isolation, error containment, link stability, and platform power behavior.
- Generated blocks are highly repetitive across functions, lanes, and ports. Review should watch for off-by-one lane/table entries, missing lane 15/table 63 endpoints, and generation drift relative to `nbio_7_0_offset.h` and `nbio_7_7_0_offset.h`.
- Status and log registers may be write-one-to-clear or otherwise side-effectful at the hardware level. The existence of an offset macro is not enough to justify generic read-modify-write behavior.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for `amdgpu/nbio_v7_2.c` and DCN 3.0.1/DCN 3.1 display resource files that include this header.
- Static cross-checks that every offset macro consumed by NBIO 7.2 code has a matching field definition in `nbio_7_2_0_sh_mask.h` where bitfield access is expected.
- Generated-data checks that repeated ranges are complete and monotonic: RC lane equalization/margining lanes 0-15, EPF0/EPF1 VF framebuffer entries VF0-VF30, EPF0/EPF1 UVD/VCE/GFX/UVD1 scheduler DW0-DW8 ranges, EPF2-EPF6 TPH steering tables 0-63, BIFPLR0 lane equalization/margining lanes 0-15, and BIFPLR0 ESM 20/25 GT/s lanes 0-15.
- Hardware or emulator register dumps on an NBIO 7.2 device comparing decoded offsets against `lspci -vvxxx`, AMDGPU debugfs register reads, and known PCIe capability-chain offsets.
- Runtime checks for NBIO 7.2 initialization paths: HDP flush offset discovery, PCIe index/data accessors, doorbell aperture setup, interrupt doorbell ranges, memory-size reporting, clock-gating/light-sleep toggles, and register remapping.
- Virtualization-focused tests on SR-IOV-capable hardware that validate EPF0/EPF1 GPU IOV mailbox, reset, VF framebuffer partition, VF resizable BAR, SR-IOV, PASID/PRI/ATS, and P2P-over-XGMI offsets.
- PCIe error and link-management tests that exercise AER reporting/clearing, DPC and RP PIO logging, ACS isolation, link retrain/equalization, 16 GT/s status, margining status, L1 PM substate controls, data link feature state, and CCIX/ESM capability handling.
