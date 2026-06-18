# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 1-2422

## Purpose

This chunk is the opening generated register-offset surface for AMD NBIO 7.7.0. It contains the license, `_nbio_7_7_0_OFFSET_HEADER` include guard, and a large set of preprocessor constants mapping symbolic PCI/PCIe/NBIO register names to byte offsets inside generated address blocks. It has no executable C logic; its role is to be included by AMDGPU NBIO 7.7 code and paired with the matching shift/mask header so driver code can address the correct hardware registers for this NBIO generation.

The covered range defines:

- `cfgNBCFG_SCRATCH_4` in `nbio_iohub_nb_nbcfg_nb_cfgdec`.
- Root-complex configuration-space offsets for `DEV0_RC`, `DEV1_RC`, and a small `DEV2_RC` subset.
- Endpoint-function configuration-space offsets for `DEV0_EPF0` through `DEV0_EPF6`.
- Complete PCIe root-port configuration blocks `BIFPLR0` and `BIFPLR1`.
- The start of `BIFPLR2`, ending at `cfgBIFPLR2_LANE_4_EQUALIZATION_CNTL_16GT` because line 2422 stops mid-block.

## Public Surface

The exported API is entirely `#define` macros. Each macro names an offset; there are no structs, enums, functions, inline helpers, or static data objects in this chunk.

The naming convention is the main interface contract:

- `cfgBIF_CFG_DEV*_RC_*` names PCI bridge/root-complex configuration fields, including identity, command/status, bus windows, PM, PCIe, MSI, slot/root controls, VC, AER, ACS, 16 GT/s PHY, and lane margining.
- `cfgBIF_CFG_DEV0_EPF*_ *` names endpoint-function PCI config and extended capability fields. `EPF0` and `EPF1` are the richest endpoint layouts; `EPF2` through `EPF6` are leaner endpoint templates.
- `cfgBIFPLR*_*` names PCIe root-port fields. In this chunk, `BIFPLR0` and `BIFPLR1` include standard bridge space and extensive PCIe extended capabilities; `BIFPLR2` is only partially included.

All address-block comments in this range show `base address: 0x0`, so consumers combine these offsets with the selected address block and the AMDGPU register-access path rather than treating them as standalone physical addresses.

## Important Register Families

`cfgNBCFG_SCRATCH_4` is a single NB config scratch offset at `0x0078`. It is separate from the PCIe config-space templates and represents general NBIO configuration scratch storage.

`DEV0_RC` and `DEV1_RC` are full root-complex/bridge templates. They expose standard PCI header bytes and words such as vendor/device ID, command, status, revision, class code, cache line, latency, header type, BIST, bridge BARs, secondary/subordinate bus numbering, IO/memory/prefetchable windows, capability pointer, ROM BAR, interrupt pins, and bridge controls. Their PCIe capability coverage includes device/link/slot/root capability and control/status fields, PCIe capability v2 fields, MSI and MSI-map, SSID, vendor-specific and virtual-channel capabilities, device serial number, AER status/mask/severity/header logs/root error/source ID, TLP prefix logs, secondary PCIe link control, per-lane equalization lanes 0-15, ACS, data link feature, 16 GT/s link/PHY status, 16 GT/s per-lane equalization, and lane margining control/status lanes 0-15.

`DEV2_RC` is a short bridge subset. It includes bus/window controls, secondary status, interrupt bridge control, slot capability/control/status, slot v2 fields, and SSID capability offsets. It is not layout-equivalent to `DEV0_RC` or `DEV1_RC`.

`DEV0_EPF0` is a comprehensive endpoint-function layout. It includes standard endpoint config space with six BARs, ROM BAR, capability pointer, interrupt line/pin, MSI and MSI-X, PCIe device/link capabilities, AER logs, resizable BAR-like BAR capability/control fields, power budget, dynamic power allocation, secondary PCIe equalization, ACS, ATS, page request/PRI-style fields, PASID, multicast, LTR, ARI, SR-IOV VF count/stride/BAR/migration fields, data link feature, 16 GT/s PHY and per-lane equalization, lane margining, VF resizable BAR capability/control fields, and an AMD GPU IOV vendor-specific block. The GPU IOV block covers SR-IOV shadow and interrupt state, reset control, hypervisor/VM mailbox doublewords, context, total framebuffer, offsets, region, P2P-over-XGMI enable, VF0 through VF30 framebuffer partition offsets, and scheduler doubleword windows for UVD, VCE, GFX, and UVD1.

`DEV0_EPF1` largely mirrors `EPF0` through the endpoint, PCIe, AER, BAR, power, DPA, ACS, ATS, page request, PASID, multicast, LTR, ARI, SR-IOV, data link, 16 GT/s, margining, and VF resizable BAR regions. Unlike `EPF0` in this chunk, it does not include the long `cfgPCIE_VENDOR_SPECIFIC_HDR_GPUIOV_*` framebuffer/scheduler block before the next address block begins.

`DEV0_EPF2` through `DEV0_EPF6` use a smaller repeated endpoint template. They include endpoint identity/header/BARs, adapter/ROM/capability pointer, PM capability, USB-like `SBRN`, `FLADJ`, and `DBESL_DBESLD` offsets, PCIe device/link capability fields, MSI/MSI-X with 32-bit and 64-bit MSI aliases, vendor-specific capability, AER logs, BAR capability/control fields, power budget, DPA substate allocation bytes, ACS, PASID, and ARI. `EPF2` additionally carries `SATA_CAP_0`, `SATA_CAP_1`, `SATA_IDP_INDEX`, and `SATA_IDP_DATA`; `EPF3` through `EPF6` omit those SATA offsets in this chunk.

`BIFPLR0` and `BIFPLR1` are complete root-port blocks in this chunk. Each contains standard bridge configuration space, PM/PCIe/MSI/SSID/MSI-map, vendor-specific capability, VC resources, device serial number, AER/root error/TLP prefix logs, secondary PCIe per-lane equalization lanes 0-15, ACS, multicast, L1 PM substates, DPC, RP PIO status/mask/severity/sys-error/exception/header/prefix logs, ESM capability/status/control/capability registers, data link feature, 16 GT/s PHY and per-lane equalization lanes 0-15, lane margining lanes 0-15, CCIX capability/control/status, 20 GT/s and 25 GT/s ESM equalization lanes 0-15, CCIX translation capability/control, and 32 GT/s link capability/control/status offsets.

`BIFPLR2` starts a third root-port block and reaches from the standard bridge header through PM, PCIe, MSI, SSID/MSI-map, vendor-specific, VC, serial number, AER/root-error/TLP prefix, secondary equalization lanes 0-15, ACS, multicast, L1 PM substates, DPC, RP PIO, ESM, data link feature, and the beginning of the 16 GT/s PHY region. The requested chunk stops at lane 4 of the 16 GT/s equalization controls, so later lines are required for the rest of `BIFPLR2`.

## Control Flow And State

There is no runtime control flow in this header. Its effective flow is compile-time substitution:

1. NBIO 7.7-aware code includes `nbio_7_7_0_offset.h`.
2. The code selects a macro for the target NBIO address block and register.
3. AMDGPU register helpers, PCIe indirect accessors, or SOC15 offset helpers combine that register symbol with an access path.
4. Bitfield extraction and composition use `nbio_7_7_0_sh_mask.h`.

The header owns no state and persists nothing. State lives in the hardware registers named by these offsets. Many named registers are stateful or side-effectful at the hardware level: bridge window configuration, MSI/MSI-X routing, AER and root error logs, DPC status, RP PIO logs, ACS isolation control, ATS/PRI/PASID enablement, SR-IOV VF sizing and BARs, GPU IOV reset/mailbox/framebuffer partition registers, L1 PM substates, link equalization, lane margining, ESM/CCIX state, and data link feature status.

## Dependencies And Integration Points

The direct peer for this header is `nbio_7_7_0_sh_mask.h`, which supplies the bit shifts and masks for registers addressed by these offsets. `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes both files and exports `nbio_v7_7_funcs` and `nbio_v7_7_hdp_flush_reg`.

`nbio_v7_7.c` uses this generated register namespace for NBIO initialization and runtime operations: HDP register remapping, revision ID extraction, memory-controller access enable, memory-size reads, SDMA/VCN/IH doorbell ranges, doorbell aperture and self-ring setup, interrupt control, HDP flush request/done offsets, PCIe index/data offsets, PCIe port index/data offsets, NBIO register initialization, medium-grain clock gating, light sleep, clock-gating state reporting, and MMIO register remap setup. Some of the symbols it consumes are outside this chunk, but they come from the same generated file and are validated as part of the same NBIO 7.7 register contract.

`amdgpu_discovery.c` selects `nbio_v7_7_funcs` and `nbio_v7_7_hdp_flush_reg` for `IP_VERSION(7, 7, 0)` and `IP_VERSION(7, 7, 1)`, so these offsets are generation-specific and should not be treated as a generic NBIO layout. `soc21.c` also has IP-version handling for NBIO 7.7 devices.

The semantic dependencies are PCI and PCI Express config-space definitions: standard type 0/type 1 headers, PM, MSI, MSI-X, PCIe capability, VC, AER, ACS, ATS, page request/PRI-style capability, PASID, multicast, LTR, ARI, SR-IOV, data link feature, 16 GT/s and 32 GT/s PHY/link capabilities, lane margining, L1 PM substates, DPC, RP PIO, ESM, and CCIX. AMD-specific dependencies include GPU IOV, framebuffer partitioning, mailbox/reset handling, P2P-over-XGMI, and scheduler register windows.

## Risks And Maintenance Notes

- This is generated hardware ABI data. A single wrong offset can make otherwise correct driver code access the wrong config register without compiler diagnostics.
- The offsets are byte offsets for config-space fields of different widths. The macro value does not encode whether the field is 8, 16, 32, or wider by convention; callers must use the correct access width.
- Several offsets intentionally alias according to PCI MSI layout rules. Examples include MSI address/data/mask/pending and 64-bit MSI variants sharing nearby offsets.
- `DEV0_RC` and `DEV1_RC` are broad root-complex layouts, while `DEV2_RC` is only a small subset. Code must not assume all root-complex device views are identical.
- `EPF0`, `EPF1`, `EPF2`, and `EPF3`-`EPF6` are not identical endpoint templates. `EPF0` carries the large GPU IOV vendor-specific region, `EPF2` has SATA IDP fields, and the later EPFs are smaller.
- Status and log registers may be write-one-to-clear or otherwise side-effectful. Generic read-modify-write on AER, DPC, RP PIO, ESM, lane margining, or link status offsets can lose diagnostic state or perturb hardware.
- Root-port controls for ACS, DPC, bridge windows, L1 PM substates, equalization, margining, ESM, CCIX, and 32 GT/s link management affect isolation, error containment, power, and link stability.
- The chunk boundary is mid-`BIFPLR2`. Any final per-file report should merge this with later chunks before claiming complete `BIFPLR2` coverage.

## Test Signals

Useful validation signals include:

- Build coverage for `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which directly includes this header and `nbio_7_7_0_sh_mask.h`.
- IP-discovery tests or boot logs showing NBIO 7.7 devices selecting `nbio_v7_7_funcs` for `IP_VERSION(7, 7, 0)` and `IP_VERSION(7, 7, 1)`.
- Static checks that consumed `cfg*` and later `reg*` names in NBIO 7.7 code have matching shift/mask definitions whenever bitfield operations are used.
- Generated-data consistency checks for repeated ranges: RC lanes 0-15, endpoint MSI/MSI-X aliases, EPF0 GPU IOV VF0-VF30 entries, EPF0 scheduler DW0-DW8 ranges, BIFPLR0/BIFPLR1 equalization and margining lanes 0-15, and BIFPLR0/BIFPLR1 ESM 20 GT/s and 25 GT/s lanes 0-15.
- Hardware or emulator register dumps on NBIO 7.7 hardware comparing PCIe capability chains and config-space offsets against `lspci -vvxxx`, AMDGPU debugfs register access, or known firmware tables.
- Runtime validation of NBIO 7.7 behaviors that depend on this generated register contract: doorbell ranges, interrupt setup, HDP flush offsets, memory-size reads, register remap setup, clock-gating and light-sleep toggles, and PCIe index/data access.
- PCIe reliability tests that exercise AER, DPC, RP PIO, ACS, link retraining/equalization, 16 GT/s and 32 GT/s status, lane margining, data link feature state, L1 PM substates, ESM, and CCIX handling.
- SR-IOV and GPU virtualization tests on capable hardware validating EPF0 GPU IOV mailbox/reset, VF framebuffer partition offsets, SR-IOV/VF BAR state, PASID/ATS/page-request behavior, and P2P-over-XGMI controls.
