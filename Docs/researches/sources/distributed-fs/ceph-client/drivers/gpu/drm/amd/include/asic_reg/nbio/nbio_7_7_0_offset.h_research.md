# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003246`: lines 1-2422, `Docs/researches/chunks/subset-b-003246_research.md`
- `subset-b-003247`: lines 2423-4876, `Docs/researches/chunks/subset-b-003247_research.md`
- `subset-b-003248`: lines 4877-7378, `Docs/researches/chunks/subset-b-003248_research.md`
- `subset-b-003249`: lines 7379-9808, `Docs/researches/chunks/subset-b-003249_research.md`
- `subset-b-003250`: lines 9809-12228, `Docs/researches/chunks/subset-b-003250_research.md`
- `subset-b-003251`: lines 12229-14645, `Docs/researches/chunks/subset-b-003251_research.md`
- `subset-b-003252`: lines 14646-17059, `Docs/researches/chunks/subset-b-003252_research.md`
- `subset-b-003253`: lines 17060-19479, `Docs/researches/chunks/subset-b-003253_research.md`
- `subset-b-003254`: lines 19480-21933, `Docs/researches/chunks/subset-b-003254_research.md`
- `subset-b-003255`: lines 21934-24299, `Docs/researches/chunks/subset-b-003255_research.md`
- `subset-b-003256`: lines 24300-26645, `Docs/researches/chunks/subset-b-003256_research.md`
- `subset-b-003257`: lines 26646-29000, `Docs/researches/chunks/subset-b-003257_research.md`
- `subset-b-003258`: lines 29001-29660, `Docs/researches/chunks/subset-b-003258_research.md`

## Chunk Research

### subset-b-003246: lines 1-2422

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

### subset-b-003247: lines 2423-4876

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 2423-4876

## Scope

This chunk is a generated AMDGPU NBIO 7.7.0 register-offset header segment. It contains preprocessor constants only: no functions, structs, enums, executable statements, locks, allocations, or software-owned storage. The range defines 2,382 macros over 2,454 source lines; 734 of those are companion `_BASE_IDX` constants used by SOC15 register helpers to select the NBIO base aperture.

The range starts in the tail of the `nbio_pcie0_bifplr2_cfgdecp` PCIe configuration-space block, covers full `cfgBIFPLR3`, `cfgBIFPLR4`, and `cfgBIFPLR5` PCIe config-space windows, then covers NBIF/BIF/RCC/GDC register blocks and the beginning of the `BIF_CFG_DEV2_RC0` config-space window. Adjacent chunks are needed for the beginning of `cfgBIFPLR2` and the remainder of `BIF_CFG_DEV2_RC0`.

## Purpose

`nbio_7_7_0_offset.h` is the address half of AMD's generated NBIO 7.7.0 register interface. It gives C code stable macro names for NBIO, BIF, RCC, GDC, and PCIe configuration registers so call sites do not hard-code numeric offsets. The matching `nbio_7_7_0_sh_mask.h` supplies field shifts and masks; this file supplies register locations and base-index metadata.

This chunk maps several classes of hardware-visible state:

- PCIe root-port or link-register config spaces (`cfgBIFPLR2` tail plus full `cfgBIFPLR3/4/5`) with standard PCI config header fields, PCIe capabilities, AER, ACS, multicast, L1 PM substates, DPC, ESM, DLF, 16 GT/s and 32 GT/s link capability registers, CCIX capability registers, equalization controls, and per-lane margining controls.
- NBIF/BIF indexed access, scratch, interrupt, MMIO remap, HDP flush, doorbell, ring buffer, mailbox, GPU IOV, address-LUT, and pad-control registers.
- RCC strap, endpoint, downstream-port, downstream-path, PF/VF, and MSIX register blocks used for revision straps, config/memory sizing, PCIe behavior, error logging, bus numbering, requester ID, peer apertures, doorbell aperture enablement, and interrupt vector programming.
- GDC doorbell and clock/power/control registers, including SDMA, CSDMA, IH, VCN, RLC, ATDMA, SDP, and NGDC power-gating controls.
- Root-complex config decode registers for `DEV0`, `DEV1`, and the beginning of `DEV2`, with 32-bit register offsets and shared base index 5.

Although this repository path is under a `ceph-client` source mirror, the file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Important Macro Families

The `cfgBIFPLR*` families describe byte offsets in PCIe configuration space. `cfgBIFPLR2` is only the high tail in this chunk: 16 GT/s lane equalization lanes 5-15, PCIe margining enhanced capability and per-lane control/status registers, CCIX/ESM capability and control registers, 20 GT/s and 25 GT/s ESM equalization registers, and 32 GT/s link capability/control/status. `cfgBIFPLR3`, `cfgBIFPLR4`, and `cfgBIFPLR5` repeat the full root-port-style layout from vendor/device IDs through extended PCIe capabilities, AER logs, lane equalization, ACS, multicast, L1 PM substates, DPC/PIO logs, ESM/DLF, 16 GT/s and 32 GT/s capability sets, CCIX, and lane margining.

The `regBIF_BX_PF0_MM_*` and `regBIF_BX_PF0_RSMU_*` constants expose PF-scoped indirect index/data windows. In `nbio_v7_7.c`, these become `get_pcie_port_index_offset` and `get_pcie_port_data_offset`, so higher AMDGPU code can reach PCIe-port/RSMU-style register spaces through the NBIO function table.

The `regBIF_BX0_*` SYSDEC block contains PCIe index/data windows, SBIOS/BIOS scratch registers, RLC/VCE/UVD interrupt controls, MMIO register CAM and remap tables, bus and interrupt controls, feature controls, BIF framebuffer enable, address LUTs, HDP remap controls, ring buffer registers, mailbox index, GPU IOV sizing, and external pad controls. `nbio_v7_7.c` directly uses `regBIF_BX0_PCIE_INDEX2`, `regBIF_BX0_PCIE_DATA2`, `regBIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL`, and `regBIF_BX0_REMAP_HDP_REG_FLUSH_CNTL`.

The `regRCC_STRAP0_*` block records BIF, port, and endpoint-function strap registers for dev0. The NBIO 7.7 implementation reads `regRCC_STRAP0_RCC_DEV0_EPF0_STRAP0` and uses a matching shift/mask macro to derive the GPU revision ID. These strap values are also natural integration points for link policy, device identity, and firmware/BIOS-programmed hardware configuration.

The RCC endpoint/downstream blocks (`regRCC_EP_DEV0_0_*`, `regRCC_DWN_DEV0_0_*`, `regRCC_DWNP_DEV0_0_*`, `regRCC_DEV0_EPF0_0_*`, and `regRCC_DEV0_0_*`) map PCIe endpoint and root-complex control state: PCIe scratch/config/error/interrupt controls, DPA power allocation, downstream link/config straps, LTR message info, function identifiers, doorbell aperture enable, config memory size, RCC error logs, bus-number lists, requester-ID restore, peer framebuffer offsets, GPU host-VM enablement, GPUIOV region, margin parameters, and reset enablement.

The BIF BIFDEC and PF blocks (`regBIF_BX0_*` and `regBIF_BX_PF0_*`) are high-value runtime integration points. They include BME and atomic error logs, doorbell self-ring GPA aperture base/control registers, HDP coherency flush and invalidate controls, GPU HDP flush request/done registers, transaction-pending status, address-LUT bypass, mailbox message buffers, mailbox interrupt control, and VM/HV mailbox registers. `nbio_v7_7.c` uses the doorbell self-ring aperture registers, HDP flush request/done offsets, HDP coherency flush remap fallback, and transaction-related flush masks from the same register family.

The `regRCC_DEV0_EPF0_0_GFXMSIX_*` block maps four graphics MSI-X vectors and the pending-bit array, including address low/high, message data, and vector control offsets. This block is register-address metadata for interrupt routing and GPU interrupt table programming.

The `regGDC0_*` block maps GDC and doorbell registers at base address `0x1400000`: SDP port controls, medium-grain clock gating, SOCCLK SDP controls, doorbell status, SDMA0/SDMA1/IH/VCN0/RLC/CSDMA doorbell ranges, ATDMA miscellaneous control, doorbell fence control, S2A miscellaneous control, and NGDC power-gating controls. `nbio_v7_7.c` programs CSDMA, VCN0, and IH doorbell ranges through these offsets.

The `regBIF_CFG_DEV0_RC0_*`, `regBIF_CFG_DEV1_RC0_*`, and partial `regBIF_CFG_DEV2_RC0_*` families are dword-addressed config decode windows at base addresses `0x10100000`, `0x10101000`, and `0x10102000`. They mirror standard PCI/PCIe config fields but collapse byte/word fields onto 32-bit register offsets. DEV0 and DEV1 are complete through lane 15 margining status in this chunk; DEV2 begins at vendor/device IDs and stops at `SLOT_CNTL2`.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the macro namespace:

- `cfgBIFPLR*_*` constants are PCI configuration-space byte offsets for BIF PCIe logical root-port windows.
- `reg...` constants are SOC15/NBIO register offsets.
- `reg..._BASE_IDX` constants select the base entry used by `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and display `NBIO_BASE(...)` style helper macros.

The macros are untyped integer literals. They do not encode access permissions, reset values, read/write width, side effects, field layout, write-one-to-clear behavior, or sequencing rules. Consumers must combine them with the matching shift/mask header and AMDGPU register access helpers.

## Control Flow

This header has no local runtime control flow. Runtime flow is imposed by AMDGPU call sites:

1. ASIC-specific code includes `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`.
2. Code chooses a macro from this header and resolves it into an MMIO address through `SOC15_REG_OFFSET`, direct SOC15 read/write helpers, PCIe-port helpers, or generated display-resource base macros.
3. For field updates, code reads a register, uses the sibling shift/mask macros through `REG_SET_FIELD` or `REG_GET_FIELD`, then writes the register back while preserving unrelated bits.
4. For doorbell, HDP flush, interrupt, PCIe config, strap, reset, or error-log state, hardware sequencing and polling behavior are owned by the consuming driver code and the NBIO hardware specification, not by this header.

Concrete NBIO 7.7 flows in this tree include HDP flush remapping, revision-ID extraction from RCC straps, MC framebuffer access enablement, memory-size reads, CSDMA/VCN/IH doorbell range programming, doorbell aperture enablement, self-ring doorbell aperture programming, IH interrupt control, PCIE index/data offset publication, HDP flush request/done offset publication, clock/power register initialization, and MMIO remap setup.

## State And Persistence Behavior

The header stores no software state and persists nothing itself. It names MMIO-backed hardware state in NBIO 7.7.

State represented by this chunk includes PCIe config-space identity/capability/error/status registers, link equalization and margining controls, CCIX/ESM/DLF/DPC/ACS capability state, BIOS scratch and mailbox registers, MMIO remap windows, address LUTs, HDP coherency and flush state, doorbell aperture and range state, GPU IOV sizing, strap-derived device/link policy, PCIe/RCC error logs, bus-number and requester-ID routing state, peer aperture offsets, GDC clock/power controls, and MSI-X vector table/PBA state.

Persistence is hardware-defined. Some values are strap or firmware initialized, some are operating-system PCI config state, some are live status latches, and some are ordinary writable MMIO controls. Values may be reset or retained differently across function-level reset, BACO, PCIe hot/warm reset, GPU reset, suspend/resume, power gating, driver reinitialization, or host firmware handoff. Error logs, pending bits, HDP flush request/done registers, doorbell ranges, and MSI/MSI-X programming are especially sensitive to reset/resume ordering.

## Dependencies And Integration Points

The direct sibling dependency is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h`, which provides field geometry for many registers named here. Other generated NBIO 7.7 headers provide related registers outside this chunk.

The main direct consumer in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`. It includes this header and exports `nbio_v7_7_funcs`, which wires offsets from this chunk into the common `amdgpu_nbio_funcs` interface. Important direct uses include:

- `regBIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL` and `regBIF_BX0_REMAP_HDP_REG_FLUSH_CNTL` for HDP remap setup.
- `regRCC_STRAP0_RCC_DEV0_EPF0_STRAP0` for revision ID extraction.
- `regGDC0_BIF_CSDMA_DOORBELL_RANGE`, `regGDC0_BIF_VCN0_DOORBELL_RANGE`, and `regGDC0_BIF_IH_DOORBELL_RANGE` for doorbell aperture assignment.
- `regRCC_DEV0_EPF0_0_RCC_DOORBELL_APER_EN` for global doorbell aperture enablement.
- `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_BASE_LOW`, `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, and `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_CNTL` for self-ring doorbell setup.
- `regBIF_BX_PF0_GPU_HDP_FLUSH_REQ`, `regBIF_BX_PF0_GPU_HDP_FLUSH_DONE`, and `regBIF_BX_PF0_HDP_MEM_COHERENCY_FLUSH_CNTL` for HDP flush and MMIO remap behavior.
- `regBIF_BX0_PCIE_INDEX2`, `regBIF_BX0_PCIE_DATA2`, `regBIF_BX_PF0_RSMU_INDEX`, and `regBIF_BX_PF0_RSMU_DATA` for PCIe/indexed register access.

Display resource files in nearby DCN families also use the broader `regBIF_BX0_*` macro pattern through `NBIO_BASE(regBIF_BX0_*_BASE_IDX) + regBIF_BX0_*`, so base-index drift in this generated header can affect display-side register address construction even when the NBIO core file is not the direct caller.

## Risks And Edge Cases

- Offset drift is silent at compile time when macro names remain stable. A wrong numeric offset or base index can read or write the wrong MMIO register while all C code still builds.
- The chunk begins and ends mid-address-space coverage. `cfgBIFPLR2` and `BIF_CFG_DEV2_RC0` are incomplete here; whole-file research must merge adjacent chunks before making complete claims about those register families.
- PCIe config offsets mix byte-addressed `cfgBIFPLR*` names with dword-style `regBIF_CFG_DEV*_RC0_*` decode windows. Consumers must use the access path expected by the macro family.
- Several macro names intentionally share the same numeric offset because multiple fields reside in the same dword, for example vendor/device ID or command/status. This is normal for register-address metadata but can look like duplication in mechanical checks.
- Doorbell and HDP registers are performance and correctness sensitive. Incorrect doorbell range size/offset, aperture base, or HDP flush request/done address can cause missed interrupts, hung queues, stale CPU/GPU memory visibility, or broken KFD interactions.
- Strap and PCIe policy registers are firmware/hardware-contract sensitive. Reprogramming them outside documented initialization paths can alter device identity, link behavior, bus numbering, requester IDs, or virtualization behavior.
- Error-log, BME, atomic, transaction-pending, MSI-X, and mailbox registers can be live or write-sensitive. Read/modify/write code must preserve reserved bits and handle clear-on-write or hardware-updated state correctly.
- GDC clock/power and doorbell registers can interact with runtime power management. Writes during power transitions or without required clock domains may fail or create resume-only bugs.
- Repeated DEV0/DEV1/DEV2 and BIFPLR3/4/5 layouts are copy/generation sensitive. A one-lane or one-device offset error can surface only on specific PCIe port, function, or lane configurations.

## Test Signals

Useful validation combines generated-header checks with hardware-oriented AMDGPU tests:

- Build AMDGPU with NBIO 7.7 support enabled. Direct macro consumers in `nbio_v7_7.c` should catch missing or renamed symbols.
- Mechanically verify that each `reg...` symbol in this chunk has the expected `_BASE_IDX` companion where SOC15 access requires one, and that base indices match the address block: PF MMIO/RSMU windows use 0/1, RCC/BIFDEC blocks mostly use 2, MSIX/GDC blocks use 3, and `BIF_CFG_DEV*_RC0` uses 5.
- Cross-check the generated offsets against AMD's authoritative NBIO 7.7.0 register database and the sibling shift/mask header so every active field layout maps to a valid address.
- Exercise boot, GPU reset, suspend/resume, runtime power management, PCIe link retraining, FLR, and AER/error paths on NBIO 7.7 hardware.
- Validate doorbell users by running SDMA, CSDMA, VCN, IH interrupt, RLC, and KFD/compute workloads; watch for missed doorbells, queue hangs, interrupt storms, or incorrect doorbell status.
- Validate HDP coherency by running CPU/GPU shared-memory and KFD workloads that require HDP flush/invalidate ordering; stale reads or hangs point at remap/flush offset problems.
- Check PCIe config-visible behavior with `lspci`, AER logs, MSI/MSI-X operation, link speed/width, L1 PM substates, DPC, ACS, and lane margining/equalization diagnostics where available.
- For virtualization/SR-IOV scenarios, test PF/VF isolation, doorbell self-ring aperture behavior, BME/atomic error handling, mailbox messaging, and FLR/recovery behavior.

## Cross-Chunk Notes

The previous chunk owns the beginning of `cfgBIFPLR2`, including the standard header and earlier PCIe capability offsets. The next chunk owns the remainder of `BIF_CFG_DEV2_RC0` after `SLOT_CNTL2`, including DEV2 MSI, PCIe extended capabilities, AER, lane equalization, margining, and higher-speed link registers. The final per-file report should reconcile those boundaries before summarizing complete NBIO 7.7 PCIe config-space coverage.

### subset-b-003248: lines 4877-7378

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 4877-7378

## Purpose

This chunk is part of AMDGPU's generated NBIO 7.7.0 register-offset header. It provides C preprocessor constants that map NBIO/BIF/RCC/SION register names to DWORD-style offsets plus a companion `_BASE_IDX` value used by AMDGPU register-access macros to select the correct register aperture/base.

The range contains 2,502 source lines and 2,394 `#define` entries: 1,197 register-offset macros and 1,197 `_BASE_IDX` macros. The count is balanced only because the chunk starts on `regBIF_CFG_DEV2_RC0_SLOT_CNTL2_BASE_IDX` without the matching offset in this chunk and ends on `regBIF_CFG_DEV0_EPF0_0_PCIE_PASID_CNTL` before its `_BASE_IDX` appears. Most base indices in this chunk are `5`, matching the NBIO aperture used by these generated headers.

At a high level, the chunk covers:

- The tail of the `BIF_CFG_DEV2_RC0` root-complex PCI/PCIe configuration image, starting at slot control/status 2 and continuing through MSI, subsystem ID, vendor-specific, VC, device serial number, AER/root error, lane equalization, ACS, DLF, 16 GT/s PHY, and lane margining offsets.
- NBIF/BIF system and PF/VF decode registers around the `0x10120000` base, including MM/PCIE index-data windows, S/BIOs scratch registers, BIF interrupt controls, GFX MMIO remap CAMs, doorbell/FB/remap/VF windows, BACO controls, power-break, PERST, scratch, and mailbox registers.
- RCC strap, endpoint, downstream, downstream-port, and device blocks for device 0/1/2, including per-function strap registers, common/device/endpoint/downstream controls, LTR/VDM/margining registers, and bus/device-number programming.
- BIF miscellaneous, reset, power, D-state, FLR, interrupt, RAS, SION arbitration/credit, and SDP/SMN virtual-wire control offsets.
- The beginning of the `BIF_CFG_DEV0_EPF0_0` endpoint-function PCI configuration image, from vendor/device identity through the first PASID capability/control offset.

The file is not executable code and has no Ceph or distributed-filesystem behavior despite its mirrored source-tree location. It is a generated hardware register contract for AMDGPU NBIO 7.7.0 code.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, or enums in this chunk. The only API surface is the generated macro convention:

- `reg<REGISTER_NAME>` gives the register offset within the address block selected by the generated base index.
- `reg<REGISTER_NAME>_BASE_IDX` gives the base-index selector passed to AMDGPU register helpers for the same register.

Important visible register families include:

- `regBIF_CFG_DEV2_RC0_*`: PCIe root-complex configuration-space offsets for device 2, root complex 0. The visible portion includes MSI message registers, SSID and MSI-map capability registers, PCIe vendor-specific and VC capabilities, device serial number, AER status/mask/severity/logs, root error command/status/source ID, TLP prefix logs, secondary PCIe capability, per-lane equalization, ACS, DLF, 16 GT/s capability/control/status, retimer/local parity mismatch status, 16 GT/s per-lane equalization, lane margining port status, and lane 0-15 margining control/status.
- `regBIF_BX_PF1_*` and `regBIF_BX1_*`: BIF indirect access, scratch, interrupt, MMIO remap, doorbell, FB, BACO, power-management, mailbox, and per-client BIF control offsets. These are internal NBIF/BIF control-plane registers rather than PCI capability registers.
- `regRCC_STRAP1_*`, `regRCC_STRAP2_*`, `regRCC_DEV*_EPF*_*`, `regRCC_DEV*_PORT_*`, `regRCC_EP_*`, `regRCC_DWN_*`, and `regRCC_DWNP_*`: reset/control/configuration straps and RCC port/endpoint/downstream registers for multiple devices and functions. These encode hardware-visible function identity, link/endpoint behavior, LTR, margining, VDM, bus numbering, and downstream-port controls.
- `regBIFC_*`, `regNBIF_*`, `regINTR_*`, `regBIF_*`, `regDEV*_PF*_*`, and `regSELF_SOFT_RST*`: miscellaneous BIF/NBIF controls for interrupt polarity/enable, outstanding VC allocation, DMA attribute overrides, PASID checking/status, performance counters, SDP/GMI/HSTARB/SMN controls, power and D-state interrupts, per-function D3hot/D0 and FLR reset controls, reset misc controls, and function D-state values.
- `regBIFL_RAS_*`: BIF leaf and central RAS control/status registers plus IOHUB RAS interrupt handling and virtual-wire forwarding offsets.
- `regSION_*`: SION client arbitration, burst target, time-slot, request/data/read-response/write-response pool credit allocation, and top-level SION control registers for clients 0-2.
- `regBIF_CFG_DEV0_EPF0_0_*`: endpoint-function PCI configuration-space offsets for device 0 EPF0. The visible range includes conventional PCI header fields, BARs, ROM BAR, capability pointer, interrupt/min-grant/max-latency fields, vendor/PM/PCIe capabilities, MSI/MSI-X, vendor-specific capability, VC capability/resource registers, device serial number, AER logs, BAR enhanced capability, power budget, DPA, secondary PCIe capability, per-lane equalization, ACS, ATS, page request, outstanding page request, and the start of PASID.

These offset macros are normally paired with the sibling `nbio_7_7_0_sh_mask.h` field definitions. Offset macros choose the register; shift/mask macros choose fields within the register value.

## Control Flow and Runtime Behavior

This header has no runtime control flow. It contributes compile-time constants that AMDGPU code uses in hardware access sequences. The implied runtime pattern is:

1. ASIC-specific initialization selects the NBIO 7.7.0 register headers.
2. A caller chooses a `reg...` offset and matching `_BASE_IDX` for the target NBIO/BIF/RCC/SION register.
3. The driver reads or writes the register through AMDGPU MMIO/SMN/config-space helpers.
4. If individual fields are needed, the caller combines the offset from this file with masks and shifts from the matching generated shift/mask header.

The represented hardware flows include PCIe root-complex and endpoint configuration, link training and equalization, 16 GT/s/PCIe PHY diagnostics, AER and RAS error reporting, interrupt/MSI/MSI-X setup, BACO/power/reset/D-state handling, FLR and D3hot-D0 reset control, mailbox and scratch communication with firmware/BIOS, address-remap/doorbell/FB window programming, DMA/PASID policy, virtual wires, SION credit/arbitration policy, and RCC strap/port/endpoint setup.

## State and Persistence

The header owns no mutable state, allocates no memory, performs no I/O, and persists nothing. It is a compile-time map of hardware state locations.

The state addressed by the macros lives in NBIO hardware registers and PCI configuration images. Some offsets point to mostly static or firmware-seeded values, such as PCI vendor/device/class/capability structures, serial-number registers, supported link and VC capabilities, strap values, and BAR capability registers. Other offsets point to live or sticky state: link status, lane equalization and margining status, AER/RAS status/log registers, D-state and reset interrupt status, PASID status, performance counters, SION credit/control state, mailbox registers, and scratch registers.

Writable state includes PCI command/device/link controls, MSI/MSI-X controls, AER masks/severity, ACS/ATS/page-request/PASID controls, DPA and power-budget controls, reset/FLR/D3hot controls, BACO/power-break/PERST controls, doorbell/FB/remap windows, DMA attribute overrides, PASID checking, virtual-wire registers, SION arbitration credits, RCC device/endpoint/downstream controls, and BIOS/firmware scratch/mailbox locations. Persistence across GPU reset, PCI reset, FLR, BACO, suspend/resume, or runtime power transitions is hardware-defined and not described by this offset header.

## Dependencies and Integration Points

The direct dependency is exact synchronization with the rest of the generated NBIO 7.7.0 register set:

- `nbio_7_7_0_sh_mask.h` supplies field masks and shifts for the values at these offsets.
- Other generated NBIO headers in the same directory provide SMN or related ASIC-register definitions.
- AMDGPU NBIO/BIF/RCC code relies on the exact `reg...` names and `_BASE_IDX` suffixes expected by local register-access helpers.

Likely integration areas include:

- NBIO 7.7.0 ASIC bring-up and low-level register read/write paths.
- PCIe root-complex and endpoint enumeration/configuration logic for `DEV2_RC0` and `DEV0_EPF0_0`.
- PCIe link management, retraining, equalization, 16 GT/s diagnostics, and lane margining code.
- MSI/MSI-X interrupt setup and PCIe AER/root-error/RAS diagnostics.
- GPU reset, per-function FLR, D3hot/D0 transition, power interrupt, BACO, PERST, and self-soft-reset handling.
- Firmware/BIOS handoff paths that use scratch, mailbox, SBIOS scratch, BIOS scratch, strap, and RCC registers.
- Virtualization and isolation-adjacent paths that depend on PASID, ATS, ACS, page-request, doorbell, VF FB, VF doorbell, and PF/VF decode windows.
- Internal fabric tuning or diagnostics that use SION credit/time-slot/burst-target controls, SDP/GMI/HSTARB controls, SMN virtual wires, and BIF performance counters.

The chunk crosses multiple address blocks with different hardware semantics even though most `_BASE_IDX` values are the same. Consumers must pair the correct register prefix with the intended hardware block; repeated names across `DEV0`, `DEV1`, `DEV2`, `EP`, `DWN`, and `DWNP` families are intentionally similar but not interchangeable.

## Risks

- Chunk boundaries split macro pairs. Line 4877 is only the `_BASE_IDX` for `regBIF_CFG_DEV2_RC0_SLOT_CNTL2`, whose offset is on the previous line outside this chunk. Line 7378 defines `regBIF_CFG_DEV0_EPF0_0_PCIE_PASID_CNTL`, whose `_BASE_IDX` follows in the next chunk. Pair-completeness checks must account for adjacent chunks.
- A wrong offset or base index silently targets the wrong hardware register. This can corrupt PCIe configuration, reset state, interrupt routing, RAS/AER policy, firmware scratch/mailbox state, or internal fabric tuning.
- Many register families are repeated by device, port, endpoint, downstream block, function, lane, or VF/PF role. Copy/paste or generated-name mistakes can map valid-looking code to the wrong device/function/lane.
- Some registers at the same offset represent different logical fields or access widths in PCI config space, such as MSI address/data aliases, status/control sharing, ACS capability/control sharing, DPA status/control sharing, and PASID capability/control sharing. Callers must use the paired shift/mask definitions and preserve unrelated bits.
- Status and log registers may have side effects such as sticky bits, write-one-to-clear behavior, destructive reads, or reset-domain-specific retention. This header does not encode access permissions or side-effect rules.
- Power/reset/D-state/FLR/BACO/PERST registers are high impact. Incorrect writes can hang the device, lose function state, or break recovery paths.
- Scratch, mailbox, and strap registers may participate in firmware contracts. Uncoordinated writes can break SBIOS/SMU/driver handoff assumptions.
- SION, DMA attribute, PASID, ATS, ACS, page-request, and virtual-wire registers can affect DMA routing, isolation, ordering, or internal fabric fairness. Incorrect programming can become a security, correctness, or performance issue.

## Test and Validation Signals

Useful validation for this chunk is mostly generated-header consistency plus hardware-facing behavior:

- Build AMDGPU configurations that include `nbio_7_7_0_offset.h` to catch malformed or duplicate macro definitions.
- Cross-check every in-range `reg...` macro against a matching `_BASE_IDX`, allowing the known first and last chunk-boundary exceptions.
- Cross-check register names against `nbio_7_7_0_sh_mask.h` so offsets have matching field definitions where the register is field-addressable.
- Compare the generated offsets and address-block boundaries with the NBIO 7.7.0 hardware register database for `bif_cfg_dev2_rc`, `bif_bx`, RCC, BIF misc/reset/RAS, SION, and `bif_cfg_dev0_epf0`.
- On matching hardware, inspect PCIe configuration dumps for `DEV2_RC0` and `DEV0_EPF0_0`; capability chains should report plausible MSI/MSI-X, VC, AER, ACS, ATS, page request, PASID, DPA, power budget, DLF, and 16 GT/s structures.
- Exercise link bring-up, retraining, equalization, 16 GT/s status, and lane margining diagnostics, confirming lane-numbered offsets map to expected lanes.
- Validate interrupt delivery through MSI/MSI-X setup and confirm mask/pending/table/PBA offsets decode correctly.
- Run reset and power-management flows such as suspend/resume, BACO, FLR, D3hot/D0 transitions, and GPU reset, checking that writable controls are restored and status bits behave as expected.
- Exercise AER/RAS error reporting or fault injection and verify uncorrectable/correctable status, root error status/source ID, header logs, TLP prefix logs, BIFL RAS central/leaf status, and IOHUB RAS interrupt controls decode consistently.
- Use firmware/BIOS handoff tests to confirm scratch, mailbox, strap, and RCC programming remain compatible with SBIOS/firmware expectations.

## Chunk Boundary Notes

Lines 4877-5143 complete the visible tail of `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp`, whose address-block comment and early PCI header offsets are above this chunk. Lines 5144-5735 cover BIF PF/system and BIFDEC1 internal blocks. Lines 5736-6517 cover large RCC strap and device/endpoint/downstream blocks for devices 0, 1, and 2. Lines 6518-6911 cover BIF miscellaneous and reset/power/D-state/FLR controls. Lines 6912-6935 cover BIF RAS controls/status. Lines 6936-7063 cover SION credit/arbitration controls. Lines 7064-7378 begin `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` and stop at the `PCIE_PASID_CNTL` offset before its `_BASE_IDX`.

### subset-b-003249: lines 7379-9808

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 7379-9808

## Scope

This chunk is part of the generated AMD NBIO 7.7.0 register-offset header used by the amdgpu driver. The selected range contains only preprocessor constants: it has no C functions, no structs, and no executable control flow. Its purpose is to give the driver stable symbolic names for NBIO/BIF PCI configuration-space register offsets and for the SOC15 base-index selector used by those registers.

The range starts in the tail of the `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` block, then defines complete blocks for `DEV0_EPF1` through `DEV0_EPF7`, and finally begins the next block, `DEV1_EPF0`. Every register constant in the chunk is paired with a `_BASE_IDX` constant whose value is `5`, indicating the same NBIO register base index for SOC15 register access macros.

## Address Blocks Covered

- `DEV0_EPF0` tail: lines 7379-7761, offsets `0x100bc` through `0x101bc`. This continues the endpoint function 0 PCIe extended-capability area rather than the normal PCI header.
- `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`: lines 7764-8277, base address `0x10141000`, offsets `0x10400` through `0x1053c`. This is a full endpoint function 1 config-space map with a richer extended-capability set than EPF2-EPF7.
- `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`: lines 8280-8525, base address `0x10142000`, offsets `0x10800` through `0x108cb`.
- `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`: lines 8528-8773, base address `0x10143000`, offsets `0x10c00` through `0x10ccb`.
- `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`: lines 8776-9021, base address `0x10144000`, offsets `0x11000` through `0x110cb`.
- `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`: lines 9024-9269, base address `0x10145000`, offsets `0x11400` through `0x114cb`.
- `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp`: lines 9272-9517, base address `0x10146000`, offsets `0x11800` through `0x118cb`.
- `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`: lines 9520-9765, base address `0x10147000`, offsets `0x11c00` through `0x11ccb`.
- `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp` start: lines 9768-9808, base address `0x10148000`, offsets `0x12000` through `0x1200b`.

The repeated spacing between endpoint-function blocks is significant. DEV0 EPF1 begins at `0x10400`, EPF2 at `0x10800`, EPF3 at `0x10c00`, and so on through EPF7 at `0x11c00`, with a `0x400` offset stride between functions. DEV1 EPF0 then starts at `0x12000`.

## Important Symbols And Register Families

This chunk contributes `1199` register-name macros and `1199` matching `_BASE_IDX` macros. The macros are consumed as compile-time constants by amdgpu register helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and PCIe indexed-access paths. The paired shift/mask details live in `nbio_7_7_0_sh_mask.h`; this header only provides addresses.

The main families are:

- PCI config common header fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, `CACHE_LINE`, `LATENCY`, `HEADER`, `BIST`, `BASE_ADDR_1` through `BASE_ADDR_6`, `CARDBUS_CIS_PTR`, `ADAPTER_ID`, `ROM_BASE_ADDR`, `CAP_PTR`, interrupt fields, and latency/grant fields.
- Capability-list blocks: vendor capability, power management (`PMI_*`), PCI Express (`PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`), MSI, and MSI-X.
- PCIe error reporting: `PCIE_ADV_ERR_RPT_ENH_CAP_LIST`, uncorrectable/correctable error status, masks, severities, AER control, header logs, and TLP prefix logs.
- BAR and address sizing: endpoint `BASE_ADDR_*`, `PCIE_BAR*_CAP`, `PCIE_BAR*_CNTL`, `PCIE_RESIZE_BAR*`, and EPF0/EPF1 VF resize BAR entries.
- Power and latency capabilities: `PCIE_LTR_*`, `PCIE_PWR_BUDGET_*`, and `PCIE_DPA_*` including DPA substate power allocation entries.
- Virtualization and isolation: `PCIE_SRIOV_*`, VF base-address entries, VF migration-state array offsets, `PCIE_ACS_*`, `PCIE_PASID_*`, and `PCIE_ARI_*`.
- Link training and signal integrity: data link feature (`DLF`), 16 GT/s PHY capability and status, lane equalization controls for lanes 0-15, and lane margining control/status for lanes 0-15.
- Miscellaneous or vendor-specific PCIe regions: `PCIE_VENDOR_SPECIFIC_*`, `FLADJ`, `DBESL_DBESLD`, and endpoint-specific capability-list anchors.

Several macros intentionally share the same offset because they name different bitfields inside the same DWORD. Examples in this range include `COMMAND`/`STATUS`, `DEVICE_CNTL`/`DEVICE_STATUS`, `LINK_CNTL`/`LINK_STATUS`, MSI address/data/mask variants, ARI cap/control, ACS cap/control, and DPA status/control. Consumers must combine these offset macros with the matching mask/shift macros rather than assuming one symbolic name equals one independent register storage location.

## Block-Specific Notes

The EPF0 tail is the broadest extended-capability slice in this chunk. It includes memory controller translation controls (`PCIE_MC_*`), latency tolerance reporting, ARI, SR-IOV, data-link features, 16 GT/s equalization, lane margining, VF resize BARs, ATS, PRI, resized BARs, secondary PCIe extended capability, protocol multiplexing, address translation service entries, and related virtualization/register-map features. Because the chunk starts on `regBIF_CFG_DEV0_EPF0_0_PCIE_PASID_CNTL_BASE_IDX`, it inherits the preceding PASID register definition from the previous chunk; merge/reconciliation should preserve that split.

The complete EPF1 block mirrors a normal PCI endpoint config-space header plus an extended capability tail. Unlike EPF2-EPF7, EPF1 includes the 16 GT/s PHY group, lane equalization entries for lanes 0-15, lane margining entries for lanes 0-15, VF resize BARs, ATS, PRI, and resize BAR controls. This suggests endpoint function 1 exposes a larger PCIe capability set than the later functions.

The EPF2 through EPF7 blocks are structurally compact and highly repetitive. Each has a standard PCI config header, vendor/PMI/PCIe/MSI/MSI-X capability entries, vendor-specific extended capability, AER logs, BAR controls, power budget, DPA, ACS, PASID, and ARI. Their offset layouts are identical apart from the `0x400` function stride.

The DEV1 EPF0 block begins only the standard config header through `ADAPTER_ID`. Later lines outside this chunk continue that address block. This chunk document should therefore not treat DEV1 EPF0 as fully covered.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is at compile time and driver initialization time:

1. `nbio_v7_7.c` includes `nbio/nbio_7_7_0_offset.h` and `nbio/nbio_7_7_0_sh_mask.h`.
2. The amdgpu discovery path assigns `nbio_v7_7_funcs` and `nbio_v7_7_hdp_flush_reg` for NBIO IP versions `7.7.0` and `7.7.1`.
3. NBIO helper functions use generated offset macros with SOC15 and PCIe register-access helpers to read, write, or return hardware register offsets.
4. For registers in this chunk, any read/write state lives in the GPU's NBIO/BIF PCI configuration hardware, not in kernel memory owned by this header.

State persistence is therefore hardware-defined. Writes through consumers can persist until reset, function-level reset, power transition, or driver/firmware reprogramming depending on the register. The header itself stores no state, allocates no memory, performs no synchronization, and has no side effects.

## Dependencies And Integration Points

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` is the direct NBIO 7.7 consumer. It includes this header and the matching shift/mask header, then publishes the `amdgpu_nbio_funcs` table used by the broader amdgpu device initialization path.
- `drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c` selects the NBIO v7.7 function table for IP versions `7.7.0` and `7.7.1`, which makes these generated constants active on matching ASICs.
- `drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h` provides bitfield definitions for the same register names. Offset-only usage is unsafe when a symbolic register shares a DWORD with other named fields.
- SOC15 helper macros and accessors provide the addressing convention. The `_BASE_IDX` value `5` is part of that convention and must remain paired with these offsets.
- The PCI and PCIe capability names map to hardware-defined config-space structures. Linux PCI core concepts such as MSI/MSI-X, SR-IOV, ACS, PASID, ATS, AER, LTR, and DPA are represented here as hardware register offsets, although this header does not implement those subsystems.

## Risks And Review Considerations

- Generated-header drift is the main risk. Incorrect offsets or missing `_BASE_IDX` pairs would compile cleanly but direct register accesses to the wrong hardware locations.
- The chunk includes many aliased offsets where different fields share one DWORD. A consumer that writes a full register without masks can corrupt adjacent fields.
- EPF2-EPF7 are repetitive with fixed strides, so copy-generation mistakes can be hard to notice in review. Validate both the function prefix and offset range when comparing revisions.
- The line range starts mid-EPF0 and ends mid-DEV1 EPF0. Any final per-file summary must account for neighboring chunks before drawing conclusions about those two blocks.
- SR-IOV, PASID, ATS, ACS, and ARI definitions are security-sensitive because they affect isolation, address translation, and virtual-function behavior. A wrong register constant can break guest isolation or DMA/IOMMU behavior even though this header has no logic itself.
- Power-management and link-training registers affect resume, clock/power states, PCIe link speed, and signal margining. Incorrect constants may show up as intermittent link instability rather than deterministic build failures.
- This file is ASIC-generation-specific. Similar NBIO or NBIF headers define related names with different offsets, so code should include the header matched to the selected IP block rather than reusing constants across generations.

## Test And Validation Signals

Useful validation is mostly integration and hardware oriented:

- Build coverage: compile the amdgpu driver for configurations that include NBIO v7.7 support to catch missing or renamed macros.
- Register-table sanity: for this chunk, verify that every non-`_BASE_IDX` macro has a matching `_BASE_IDX` macro and that the base index remains `5`.
- Layout checks: compare EPF1-EPF7 address ranges against the ASIC register database or generated source, especially the `0x400` endpoint-function stride and the EPF2-EPF7 repeated layouts.
- Runtime smoke tests on NBIO IP `7.7.0` or `7.7.1`: device probe, PCIe link reporting, MSI/MSI-X interrupt operation, suspend/resume, SR-IOV capability exposure where supported, and AER logging.
- Targeted register access tests: use existing amdgpu debug paths or controlled driver instrumentation to read selected config-space offsets from EPF1-EPF7 and confirm expected PCI capability IDs/next pointers.
- Negative signal: unexplained PCI capability-list corruption, invalid BAR sizing, failed MSI/MSI-X setup, broken VF enumeration, ACS/PASID/ATS exposure mismatches, or AER logs with impossible header data can indicate offset mismatch in this family.

### subset-b-003250: lines 9809-12228

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 9809-12228

## Chunk Scope

- Work item: `subset-b-003250`
- Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, lines 9809-12228
- Parent file role: generated AMDGPU NBIO 7.7.0 register offset map.
- Chunk shape: 2,420 source lines containing 2,396 `#define` entries, 1,198 register-offset symbols, and 1,198 `*_BASE_IDX` definitions. Every base-index value in this span is `5`.

This is generated hardware ABI data, not executable driver logic. The constants are consumed by AMDGPU NBIO code through SOC15 register access helpers and paired with `nbio_7_7_0_sh_mask.h` when callers need bitfield-safe reads or writes.

## Purpose

This chunk defines symbolic register indexes for several NBIF/BIF PCI configuration-space windows and PCIe logical-root-port windows in NBIO 7.7.0 hardware. The values identify where standard PCI header fields, PCIe capability structures, MSI/MSI-X state, Advanced Error Reporting, virtualization capabilities, lane diagnostics, power-management capabilities, and root-port error-containment registers live inside AMD's generated register map.

The covered address blocks are:

- Continuation of `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp` from the previous chunk, starting at `regBIF_CFG_DEV1_EPF0_0_ADAPTER_ID_BASE_IDX` and then `ROM_BASE_ADDR` through ARI control.
- Complete visible `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`, base address `0x10149000`, from endpoint identity through ARI control.
- Complete visible `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`, base address `0x10150000`, from endpoint identity through ARI control.
- Complete visible `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp`, base address `0x10151000`, from endpoint identity through ARI control.
- Complete visible `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp`, base address `0x10152000`, from endpoint identity through ARI control.
- Complete visible `nbio_pcie0_bifplr0_cfgdecp`, base address `0x11100000`, from logical root-port identity through 32 GT/s link status.
- Beginning of `nbio_pcie0_bifplr1_cfgdecp`, base address `0x11101000`, from logical root-port identity through `PCIE_RP_PIO_HDR_LOG2`; the rest of that root-port block continues in the next chunk.

## Public Surface

There are no C functions, structs, enums, callbacks, variables, or inline helpers in this range. The public surface is entirely preprocessor macros:

- `reg...` macros, such as `regBIF_CFG_DEV2_EPF0_0_PCIE_UNCORR_ERR_STATUS`, `regBIF_CFG_DEV1_EPF1_0_PCIE_PASID_CNTL`, `regBIFPLR0_0_PCIE_DPC_STATUS`, and `regBIFPLR1_0_PCIE_RP_PIO_HDR_LOG2`, define register indexes.
- Matching `reg..._BASE_IDX` macros define the SOC15 base-table index for the register. In this chunk all are `5`, which means consumers rely on NBIO base slot 5 when computing the final MMIO address.
- Many logical names intentionally share the same numeric register index because PCI config-space fields are narrower than a DWORD or because a single DWORD has status/control or capability/control views. Examples include vendor/device ID pairs, command/status pairs, MSI data/address overlays, capability/control pairs, lane pairs, and DPA substate allocation groups.

The register-index range visible in this chunk starts at `0x1200c` for `regBIF_CFG_DEV1_EPF0_0_ROM_BASE_ADDR` and reaches `0x4004ea` for `regBIFPLR1_0_PCIE_RP_PIO_HDR_LOG2`. The chunk has two deliberate cross-boundary incompletenesses: line 9809 is only the `BASE_IDX` for `regBIF_CFG_DEV1_EPF0_0_ADAPTER_ID` from the previous line, and line 12228 defines `regBIFPLR1_0_PCIE_RP_PIO_HDR_LOG2` while its `_BASE_IDX` appears just after the requested range.

## Important Register Families

The endpoint-function blocks under `BIF_CFG_DEV1_*` and `BIF_CFG_DEV2_*` map PCI endpoint configuration images. They include standard header registers such as vendor/device ID, command/status, revision/class code, cache-line/latency/header/BIST, BARs, ROM BAR, capability pointer, interrupt line/pin, and adapter/vendor capability fields.

Their PCIe capability areas include:

- Power management capability and status/control registers.
- PCIe device, link, and device/link capability 2 controls and status.
- MSI and MSI-X structures, including message control, address/data, masks, pending bits, MSI-X table, and PBA offsets.
- Vendor-specific enhanced capabilities and virtual-channel capability/resource registers.
- Advanced Error Reporting status, masks, severity, capability/control, header logs, and TLP prefix logs.
- BAR enhanced capability/control, power budget, dynamic power allocation substate allocation, secondary PCIe capability, ACS, PASID, and ARI controls.

The `DEV1_EPF0` part starts mid-block, so its earliest identity/header/BAR macros are in the previous chunk. `DEV1_EPF1`, `DEV2_EPF0`, `DEV2_EPF1`, and `DEV2_EPF2` are visible from their `VENDOR_ID` definitions onward. The `DEV2` endpoint blocks follow the same repeated generated layout pattern with offsets shifted by endpoint/function window.

The `BIFPLR0_0` block is a PCIe logical-root-port configuration image. It includes bridge-oriented PCI fields such as bus-number and window registers, root/slot controls, PM/PCIe/MSI/SSID/MSI-map capability structures, vendor-specific capability, VC resources, device serial number, AER/root-error status, secondary PCIe equalization controls, ACS, multicast capability, L1 PM substates, DPC, RP PIO error reporting and logs, ESM capability/status/control, data-link feature capability/status, 16 GT/s PHY controls and per-lane equalization, margining port/lane controls, CCIX transaction capability/control, ESM 20 GT/s and 25 GT/s per-lane equalization controls, and 32 GT/s link capability/control/status registers.

The `BIFPLR1_0` block begins the same root-port pattern for the second logical root port. This chunk covers its standard bridge header, PM/PCIe/MSI/SSID/MSI-map capability area, VC resources, device serial number, AER/root-error logging, secondary PCIe equalization for lanes 0-15, ACS, multicast controls, L1 PM substates, DPC, and the start of RP PIO logging through header log 2.

## Control Flow

This header has no runtime control flow. The operational flow is external:

1. NBIO 7.7.0 driver code includes `nbio_7_7_0_offset.h` and the sibling shift/mask header.
2. Code selects a `reg...` symbol for a hardware operation.
3. SOC15 helpers combine the offset, the `*_BASE_IDX`, NBIO hardware instance, and generated base table into an MMIO address.
4. Driver code reads, writes, or polls that address through helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, or PCIe-port accessors.
5. Field composition or decoding uses `REG_SET_FIELD` and masks/shifts from `nbio_7_7_0_sh_mask.h`.

The values in this chunk can therefore alter runtime behavior only through consumers. Incorrect constants can redirect an otherwise correct driver operation to the wrong register.

## State And Persistence

The file owns no mutable state, allocates no memory, performs no I/O, and persists nothing. It names hardware state in NBIO/NBIF PCI configuration and logical-root-port windows.

The represented hardware state includes:

- Endpoint identity, class, BAR, ROM, capability-list, interrupt, PM, MSI, MSI-X, AER, VC, ACS, PASID, ARI, power-budget, and DPA state.
- Root-port bridge windows, bus numbering, root/slot controls, link controls, link status, negotiated link width/speed, L1 PM substate controls, DPC state, RP PIO error state, and AER root-error logs.
- Lane-level state for equalization, 16 GT/s PHY training/status, margining control/status, ESM 20/25 GT/s equalization, and 32 GT/s link control/status.
- Error-observation and error-policy state, including correctable/uncorrectable masks, severities, header logs, TLP prefix logs, DPC status, RP PIO masks/severity/sys-error/exception bits, and error source IDs.

Persistence across FLR, GPU reset, PCIe hot reset, suspend/resume, runtime power transitions, or BACO is not encoded here. Those behaviors are defined by hardware and by the driver code that uses these offsets.

## Dependencies And Integration Points

The direct companion header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h`, which supplies bit positions and masks for many registers named here. Offsets alone are sufficient for raw reads/writes but not for safe field manipulation.

The direct source-tree user found for this header is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. That implementation uses the generated register macros for NBIO 7.7 operations such as HDP register remapping, revision-ID reads, framebuffer access enablement, memory-size reads, SDMA/VCN/IH doorbell range programming, doorbell aperture setup, PCIE/RSMU index/data offset lookup, interrupt control, and NBIO initialization.

The specific endpoint and root-port macros in this chunk are likely used indirectly by common AMDGPU PCIe/NBIO access paths, diagnostics, dumps, or future feature code rather than all being referenced directly in `nbio_v7_7.c`. Their integration contract is the generated naming convention plus the SOC15 base-index convention.

These definitions also integrate conceptually with PCI and PCIe configuration-space specifications: PM, MSI, MSI-X, PCIe device/link/slot/root capabilities, VC, AER, ACS, PASID, ARI, power budget, DPA, multicast, L1 PM substates, DPC, RP PIO, data-link feature, 16 GT/s and 32 GT/s link capabilities, and lane margining.

## Risks And Edge Cases

- Chunk boundaries split two macro pairs. `regBIF_CFG_DEV1_EPF0_0_ADAPTER_ID_BASE_IDX` lacks its register macro inside this exact range, and `regBIFPLR1_0_PCIE_RP_PIO_HDR_LOG2` lacks its `_BASE_IDX` until the next line after the range. Pair-completeness checks must be performed after adjacent chunks are reconciled.
- Generated aliases are intentional. Removing duplicate numeric values or assuming one unique register per macro would break PCI config fields that share DWORDs or have multiple semantic views.
- The endpoint blocks are repetitive across devices/functions. Accidentally mixing `DEV1` and `DEV2`, or `EPF0`, `EPF1`, and `EPF2`, can compile cleanly while targeting a different PCI function image.
- Root-port blocks are similarly repetitive. Using a `BIFPLR0_0` macro for a `BIFPLR1_0` access can misread or reprogram the wrong logical root port.
- Base index `5` is part of the ABI. Copying a macro name or offset into code that bypasses the matching `*_BASE_IDX` can compute the wrong SOC15 address.
- AER, DPC, RP PIO, and root-error registers are error-handling critical. Wrong offsets can mask fatal errors, fail to clear sticky status, misattribute PCIe faults, or produce misleading diagnostics.
- Link-control, 16 GT/s, 25 GT/s ESM, margining, and 32 GT/s registers affect link stability and performance. Incorrect writes can disrupt training, power management, equalization, or recovery.
- ACS, PASID, ARI, multicast, VC, and MSI/MSI-X controls affect routing, isolation, interrupt delivery, and virtualization behavior. Mistakes can cause security, enumeration, or interrupt-routing failures.
- Status/log registers may have hardware side effects such as write-one-to-clear semantics. This header does not encode access width or side-effect policy; consumers must use the matching hardware programming guide and driver conventions.

## Test And Validation Signals

Useful validation for this chunk is mostly generated-data and hardware integration coverage:

- Build AMDGPU with NBIO 7.7.0 support so `nbio_v7_7.c` and dependent headers resolve all referenced offset and mask symbols.
- Static generated-header checks should verify that every visible `reg...` has a matching `reg..._BASE_IDX` after adjacent chunks are merged, and that all base indices in this range remain `5`.
- Cross-check register families against `nbio_7_7_0_sh_mask.h` so field-level users have matching mask/shift definitions for endpoint, root-port, AER, DPC, MSI/MSI-X, link, ACS, PASID, ARI, and lane diagnostics registers.
- Compare generated endpoint layouts across `DEV1_EPF1`, `DEV2_EPF0`, `DEV2_EPF1`, and `DEV2_EPF2` for expected structural symmetry and offset deltas.
- Compare `BIFPLR0_0` and `BIFPLR1_0` common root-port layouts where both are visible, while accounting for this chunk ending before `BIFPLR1_0` is complete.
- Runtime smoke tests on matching hardware should cover GPU probe, NBIO revision read, framebuffer access enable/disable, doorbell aperture/range setup, HDP flush remap paths, interrupt setup, reset, suspend/resume, and PCIe link stability.
- PCIe validation should include AER/DPC/RP PIO error injection or controlled error paths, checking status/mask/severity/log decoding and clearing behavior.
- Virtualization and IOMMU tests should validate PASID, ARI, ACS, MSI/MSI-X, BAR, and endpoint-function enumeration behavior when the relevant functions are exposed.
- Link diagnostics should exercise lane equalization, L1 PM substates, 16 GT/s status, ESM 20/25 GT/s lane controls, margining, and 32 GT/s link capability/status paths where supported by hardware or simulation.

## Notes For Merge/Reconciliation

This is one chunk of the larger `nbio_7_7_0_offset.h` file. It should remain source-tree-aligned under `Docs/researches/chunks/` and should not be treated as a final per-file report.

The merge lane should preserve the fact that lines 9809-10200 continue `DEV1_EPF0` from the previous chunk, lines 10202-11371 cover additional endpoint-function blocks, lines 11374-11923 cover complete visible `BIFPLR0_0`, and lines 11926-12228 start but do not complete `BIFPLR1_0`.

### subset-b-003251: lines 12229-14645

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 12229-14645

## Chunk Scope

- Work item: `subset-b-003251`
- Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h`, lines 12229-14645
- Parent file role: generated AMDGPU NBIO 7.7.0 register offset map used by SOC15/NBIO register access helpers.
- Chunk shape: 2,397 preprocessor definitions. Most are paired `reg*` register-offset and `reg*_BASE_IDX` macros; this slice starts with a dangling `BIFPLR1_0` base-index macro from a prior register and ends after the first three `BIFP3_0` register offsets. Every visible `*_BASE_IDX` in the chunk is `5`.

## Purpose

This chunk supplies symbolic offsets for NBIO 7.7.0 PCIe logical-root-port and PCIe direct/link-controller register spaces. It does not implement executable behavior. Its purpose is to let AMDGPU code refer to hardware registers by generated names instead of numeric MMIO offsets, then let helpers such as `SOC15_REG_OFFSET(NBIO, instance, reg...)`, `RREG32_SOC15(...)`, `WREG32_SOC15(...)`, `RREG32_PCIE_PORT(...)`, and `WREG32_PCIE_PORT(...)` resolve and access the correct address.

The chunk is split between two major hardware views. `BIFPLR*_0` blocks model PCIe configuration-space-like logical root ports with standard PCI/PCIe capability registers, AER/DPC/error-reporting registers, link-speed capability extensions, lane equalization, link margining, CCIX/ESM, and 32 GT status. `BIFP*_0` blocks model PCIe direct link/transaction registers for individual ports, including link controller state, speed/width controls, L1 PM substate save/restore, RX/TX credits, replay/NAK state, and flow-control counters.

## Major Register Families In This Chunk

- Lines 12229-12475 finish the `BIFPLR1_0` logical-root-port configuration group from the previous chunk. The visible portion covers RP PIO header/prefix logs, ESM capability/status/control registers, data-link feature registers, 16 GT PHY/link capability and equalization registers, per-lane margining control/status for lanes 0-15, CCIX and ESM capability/control/status registers, 20 GT and 25 GT ESM lane equalization tables, CCIX transaction capability/control, and 32 GT link capability/control/status.
- Lines 12478-13027 define `nbio_pcie0_bifplr2_cfgdecp` at base address `0x11102000`. This is a full logical-root-port config decode block. It starts with PCI identity and command/status aliases, bridge-window registers, capability pointers, power-management capability registers, PCIe capability/link/slot/root registers, MSI registers, vendor-specific capability registers, virtual-channel resources, device serial number, AER status/mask/severity/logging, secondary PCIe capability registers, lane equalization tables, ACS, multicast, L1 PM substates, DPC, RP PIO error reporting/logging, ESM, data-link feature, 16 GT link/equalization, margining, CCIX/ESM, 20 GT/25 GT equalization, CCIX transaction, and 32 GT link status.
- Lines 13030-13579 define `nbio_pcie0_bifplr3_cfgdecp` at base address `0x11103000`. It repeats the same logical-root-port layout as `BIFPLR2_0`, giving a separate offset namespace for another PCIe root port.
- Lines 13582-14131 define `nbio_pcie0_bifplr4_cfgdecp` at base address `0x11104000`. It repeats the same full config-space/logical-root-port register families for a fourth port namespace.
- Lines 14134-14300 define `nbio_pcie0_bifp0_pciedir_p` at base address `0x11140000`. This direct PCIe port block contains scratch/reserved registers, port control, TX requester ID, physical lane status, error control, RX controls and expected sequence number, RX allocated credits for posted/non-posted/completion traffic, physical/transaction error injection registers, NAK counter, link controller control/training/width/speed/state registers, link-controller L1 PM substate registers, BCH ECC control, clock-gating override, save/restore registers, speed-control extensions, TX sequence/replay/latency/request-number controls, TX advertised/init credit registers, credit status, and flow-control counters for VC0 and VC1.
- Lines 14302-14468 define `nbio_pcie0_bifp1_pciedir_p` at base address `0x11141000`, repeating the `BIFP0_0` PCIe direct-port layout for port 1.
- Lines 14470-14635 define `nbio_pcie0_bifp2_pciedir_p` at base address `0x11142000`, repeating the `BIFP0_0` PCIe direct-port layout for port 2.
- Lines 14638-14645 begin `nbio_pcie0_bifp3_pciedir_p` at base address `0x11143000`, but this chunk only includes `PCIEP_RESERVED`, `PCIEP_SCRATCH`, and `PCIEP_PORT_CNTL` plus base-index macros. The rest of `BIFP3_0` continues in the next chunk.

## Important APIs, Types, And Symbols

There are no C functions, structs, enums, or storage objects in this slice. The public interface is preprocessor constants:

- Register-offset macros such as `regBIFPLR2_0_VENDOR_ID`, `regBIFPLR3_0_PCIE_UNCORR_ERR_STATUS`, `regBIFPLR4_0_PCIE_DPC_STATUS`, `regBIFPLR1_0_LINK_STATUS_32GT`, `regBIFP0_0_PCIE_LC_SPEED_CNTL`, `regBIFP1_0_PCIE_LC_LINK_WIDTH_CNTL`, and `regBIFP2_0_PCIE_TX_CREDITS_STATUS`.
- Paired base-index macros such as `regBIFPLR2_0_LINK_STATUS_16GT_BASE_IDX` and `regBIFP2_0_PCIE_LC_CNTL_BASE_IDX`, all set to `5` in this chunk. SOC15 offset machinery depends on these indices to select the generated base for the NBIO register block.
- PCIe configuration-space aliases in the `BIFPLR*_0` groups. Several names intentionally share the same DWORD offset because they represent different field views of a PCI/PCIe config register, for example command/status, device control/status, link control/status, slot control/status, and capability/status pairs.
- Per-lane table symbols for equalization and margining. Four lanes are packed per equalization DWORD in several 16 GT/20 GT/25 GT tables, so lane-specific macro names can intentionally map to the same offset.
- PCIe direct-port link-controller symbols in the `BIFP*_0` groups, especially `PCIE_LC_*`, `PCIE_RX_*`, `PCIE_TX_*`, `PCIE_FC_*`, `PCIEP_STRAP_*`, and error-injection/counter symbols.

## Control Flow

The header itself has no executable control flow. Runtime flow is data-driven:

1. NBIO or PCIe-related driver code selects a generated register symbol for the ASIC generation it is compiling against.
2. `SOC15_REG_OFFSET` combines the symbol's offset, the `*_BASE_IDX` metadata, the NBIO IP block, and the instance number into an MMIO register address.
3. AMDGPU register helpers read, write, or poll that address directly or through PCIe index/data windows.
4. For bit-level operations, code combines these offsets with matching shift/mask definitions from `nbio_7_7_0_sh_mask.h` and helpers such as `REG_SET_FIELD` or `REG_GET_FIELD`.

`amdgpu/nbio_v7_7.c` is the visible NBIO 7.7.0 integration point. It includes this offset header and the matching mask header, then uses SOC15 and PCIe-port helpers for NBIO setup, HDP flush offsets, PCIe index/data offsets, doorbell ranges, interrupt control, register remapping, memory-controller access, and BIF clock-gating/light-sleep configuration. This exact chunk's root-port and direct-port symbols are primarily a generated hardware ABI surface for PCIe link/error/debug paths rather than ordinary procedural code.

## State And Persistence Behavior

The source file has no mutable software state and persists no data. The registers it names are hardware state:

- Logical-root-port identity, bridge-window, capability, MSI, VC, ACS, multicast, DPC, ESM, CCIX, and link-speed registers represent PCIe configuration-space state for multiple root-port namespaces.
- AER, DPC, RP PIO, ESM, lane-error, parity-mismatch, NAK, replay, and credit-status registers expose transient or sticky hardware error/status state. Some status bits may require write-one-to-clear or firmware/driver policy outside this header.
- Link controller, speed, width, training, FTS, CDR, equalization, margining, L1 PM substate, save/restore, and clock-gating override registers affect link training, power-management, and resume behavior until reprogrammed or reset.
- RX/TX credit and flow-control registers reflect or configure transaction-layer resource accounting. Incorrect writes can alter PCIe throughput or stability.
- Error-injection registers are test/debug controls and must not be confused with passive status registers.

Persistence risk is therefore not in the generated header text itself. The operational risk is stale or mismatched offsets causing a driver, debug tool, or firmware interface to read the wrong status or mutate the wrong hardware state.

## Dependencies And Integration Points

- Included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which binds NBIO 7.7.0 register offsets to the `amdgpu_nbio_funcs` operations for HDP flush, PCIe index/data access, doorbells, interrupts, memory access, clock gating, light sleep, and setup.
- Depends on the matching `nbio_7_7_0_sh_mask.h` for field layouts. Offset macros identify register addresses; mask/shift macros identify the meaning of bits within those registers.
- Depends on the AMDGPU SOC15 register-base infrastructure. The numeric offset plus `BASE_IDX == 5` only has meaning when paired with the generated NBIO base tables used by `SOC15_REG_OFFSET`.
- Integrates with generic AMDGPU register-access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.
- Related NBIO versions (`nbio_7_2_0_offset.h`, `nbio_7_9_0_offset.h`, `nbio_7_11_0_offset.h`, and nearby generated headers) contain similarly named symbols with generation-specific offsets. Code must include the header matching the active NBIO IP version rather than carrying offsets across ASIC generations.
- Power-management and diagnostics can consume the PCIe link-state concepts exposed here. Even when newer NBIO 7.7.0 code does not name every `BIFP*_0` or `BIFPLR*_0` symbol directly, register dump, debug, link-training, and validation tools rely on the generated map being faithful.

## Risks And Edge Cases

- The chunk starts and ends inside address blocks. It begins with `regBIFPLR1_0_PCIE_RP_PIO_HDR_LOG2_BASE_IDX` after the matching offset from the prior chunk and ends after only the first three `BIFP3_0` registers. The merge lane must preserve cross-chunk continuity.
- All visible base indices are `5`. A generator drift that changes only an offset or only a base index can compile successfully but target a wrong MMIO address.
- The logical-root-port blocks are highly repetitive across `BIFPLR2_0`, `BIFPLR3_0`, and `BIFPLR4_0`. Off-by-one lane entries, missing lane 15 entries, wrong port prefixes, or incorrect offset progression would be hard to notice in review and could affect only one port.
- Aliased offsets are intentional for many PCIe config-space views and lane-packed registers. Automated de-duplication or "unique offset" validation would produce false positives unless it understands these shared DWORD layouts.
- Link-training and equalization registers are sensitive. Wrong offsets in `LINK_CNTL_*`, `LINK_STATUS_*`, 16 GT/20 GT/25 GT equalization, or margining controls can lead to link-speed negotiation failures, degraded width, intermittent PCIe errors, or misleading diagnostics.
- Error-reporting registers are policy-critical. Misaddressed AER, DPC, RP PIO, ESM, or parity/status registers can hide fatal errors, report the wrong source, or leave sticky errors uncleared.
- Direct-port `PCIE_RX_*`, `PCIE_TX_*`, credit, replay, NAK, and flow-control registers are transaction-layer sensitive. Incorrect writes can cause data-path stalls or severe performance regressions; incorrect reads can send debugging toward the wrong link layer.
- Error-injection registers in the `BIFP*_0` blocks are adjacent to passive status/counter registers. Test code should gate writes carefully and avoid exposing these symbols through broad "poke all registers" flows.

## Test And Validation Signals

- Build coverage: compile AMDGPU with NBIO 7.7.0 support and verify `nbio_v7_7.c` resolves this header and the matching mask header without symbol drift.
- Generated-header consistency: check that every `reg*` macro in this span has the expected paired `reg*_BASE_IDX`, that visible base indices are `5`, and that known alias groups are intentional.
- Cross-generation comparison: mechanically compare repeated `BIFPLR*_0` and `BIFP*_0` families against AMD's source register database and nearby NBIO headers to catch copied offsets from the wrong generation.
- Runtime probe on matching hardware: successful driver initialization, HDP flush setup, doorbell setup, interrupt delivery, memory-controller access enablement, and BIF clock-gating/light-sleep toggles indicate the surrounding NBIO map is coherent.
- PCIe link validation: exercise link speed/width negotiation, retraining, suspend/resume, L1 PM substates, 16 GT/32 GT status reads, equalization status, and margining diagnostics on every exposed port.
- Error-path validation: use controlled PCIe AER/DPC/RP PIO/ESM and parity/error-injection tests where supported, then verify status, mask, severity, source-id, header-log, prefix-log, NAK, replay, and counter registers report sane values and clear as expected.
- Diagnostic validation: register dumps should show coherent per-port namespaces for `BIFPLR1_0` through `BIFPLR4_0` and `BIFP0_0` through `BIFP3_0`; port 2 should not mirror port 1 unexpectedly, and packed lane registers should decode lanes consistently.

## Notes For Merge/Reconciliation

- This is a chunk-level report only for `subset-b-003251`; no final per-file report was produced.
- The chunk begins inside the previous `BIFPLR1_0` block and should be merged with the prior chunk for the complete `BIFPLR1_0` story.
- The chunk ends at the start of `BIFP3_0`; the next chunk should continue the direct PCIe port 3 register family.
- Keep this report under `Docs/researches/chunks/` and let the merge/reconciliation lane create the source-tree-aligned final document after all chunks for `nbio_7_7_0_offset.h` are available.

### subset-b-003252: lines 14646-17059

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 14646-17059

## Purpose

This chunk is an auto-generated AMD NBIO 7.7 register-offset slice for PCIe/NBIO hardware blocks. It contains no executable C logic. Its purpose is to publish preprocessor constants that map symbolic register names to NBIO 7.7 register offsets, plus the matching `*_BASE_IDX` values used by SOC15 register-access helpers.

The selected line range starts in the middle of the `nbio_pcie0_bifp3_pciedir_p` block, covers the complete `nbio_pcie0_bifp4_pciedir_p` block, covers the global `nbio_pcie0_pciedir` block, covers complete `nbio_pcie1_bifplr0_cfgdecp`, `bifplr1`, and `bifplr2` PCIe link-root/config-decode blocks, and ends at the beginning of `nbio_pcie1_bifplr3_cfgdecp`.

## Public Surface In This Chunk

The public surface is 2,390 `#define` macros: 1,195 register offset macros and 1,195 matching `*_BASE_IDX` macros. Every `*_BASE_IDX` value in this range is `5`, so consumers rely on these constants as part of the SOC15 address-space tuple rather than as independently computed values.

Macro families in this range are:

- `regBIFP3_0_*`: tail of PCIe port 3 directory-port registers, beginning at `PCIE_TX_REQUESTER_ID` and covering lane status, receive controls, flow-control credits, error injection, link-control state, link training/speed/width, straps, L1 PM substates, equalization controls, save/restore registers, transmit sequence/replay, and advertised/initialized flow-control credits.
- `regBIFP4_0_*`: complete PCIe port 4 directory-port register set with the same structure as the port 3 tail, starting at `PCIEP_RESERVED`, `PCIEP_SCRATCH`, and `PCIEP_PORT_CNTL`.
- `regBIF0_*`: global PCIe/NBIO directory registers at base `0x11180000`, including PCIe control/status/debug, common AER mask, last received TLP logs, link power-management controls, physical-layer and SDP controls, clock-request mapping, performance counters, SW reset request/status/masking, LC/HP/CPM controls, straps, SMN/SMU fenced registers, master request/error controls, and HIP registers.
- `regBIFPLR0_1_*`, `regBIFPLR1_1_*`, and `regBIFPLR2_1_*`: complete PCIe root-port/link-root configuration decode maps for PCIe1 blocks at bases `0x11200000`, `0x11201000`, and `0x11202000`.
- `regBIFPLR3_1_*`: beginning of the next PCIe1 link-root config-decode map at base `0x11203000`, from vendor/device ID through `ROOT_CNTL`.

There are no functions, structs, enums, inline helpers, or data objects here. The API contract is the exact macro spelling and numeric value, synchronized with the companion `nbio_7_7_0_sh_mask.h` field definitions and AMD's generated NBIO 7.7 register database.

## Register Coverage

The `BIFP3_0` and `BIFP4_0` directory-port portions describe per-port PCIe datapath registers. These cover data-link transmit/receive state (`PCIE_TX_SEQ`, `PCIE_TX_REPLAY`, `PCIE_RX_EXPECTED_SEQNUM`), credit allocation/advertisement (`RX_CREDITS_ALLOCATED_*`, `TX_CREDITS_*`, `PCIE_FC_*`), error control and injection (`PCIE_ERR_CNTL`, `PCIEP_ERROR_INJECT_*`, `PCIEP_NAK_COUNTER`), link-controller state and policy (`PCIE_LC_CNTL*`, `PCIE_LC_STATE*`, `PCIE_LC_SPEED_CNTL*`, `PCIE_LC_LINK_WIDTH_CNTL`), link equalization (`PCIE_LC_FORCE_COEFF*`, `PCIE_LC_BEST_EQ_SETTINGS`, `PCIE_LC_FORCE_EQ_REQ_COEFF*`), and low-power link behavior (`PCIE_LC_L1_PM_SUBSTATE*`, clock-gate override, save/restore registers).

The `BIF0` global block describes the shared PCIe directory and NBIO control surface. It includes broad PCIe control and diagnostics, AER policy, RX/TX logging, power-management controls, physical-port status, I2C sideband access registers, SDP slave attributes, performance counter controls for multiple TX clocks, software-reset controls and status, register-write activity tracking, link-controller/hotplug/clock-power-management knobs, strap shadow registers, master request sizing/error controls, and SMU/SMN integration registers.

Each complete `BIFPLR*_1` block repeats a PCI/PCIe configuration-space layout for a link-root/root-port function:

- Conventional PCI bridge header: vendor/device ID, command/status, revision/class bytes, cache-line/latency/header/BIST, secondary/subordinate bus information, I/O/memory/prefetchable windows, ROM BAR, interrupt line/pin, and bridge controls.
- Capability structures: vendor capability, power-management capability/status, PCIe capability, device/link/slot/root control and status, second-generation device/link/slot capability registers, MSI, SSID, MSI map, and vendor-specific enhanced capability.
- Advanced PCIe features: virtual-channel controls, AER status/mask/severity/logging, ACS controls, latency tolerance reporting, L1 PM substates, second vendor-specific capability payload, DPC capability/control/status, resizable BAR, and local error status/masking/severity/injection.
- High-speed link tuning: 16 GT/s link and lane equalization registers, lane margining controls/status for lanes 0 through 15, CCIX/ESM capability and control registers, 20 GT/s and 25 GT/s ESM lane equalization groups, and 32 GT/s link capability/control/status.

The `BIFPLR3_1` portion is intentionally partial in this chunk. It only covers the start of the conventional PCI/PCIe header through `ROOT_CNTL`; `ROOT_CAP`, `ROOT_STATUS`, MSI, AER, equalization, margining, CCIX/ESM, and 32 GT/s registers for this block continue after line 17059.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A translation unit includes `nbio/nbio_7_7_0_offset.h`, usually alongside `nbio/nbio_7_7_0_sh_mask.h`.
2. Driver code selects a register macro, often through `SOC15_REG_OFFSET(NBIO, instance, reg...)` or through helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT`.
3. The numeric offset and base index are resolved by the compiler into the register-access helper call.
4. Actual reads, writes, polling, reset observation, and bit manipulation occur in AMDGPU/NBIO code outside this header.

The header stores no software state and persists nothing. Persistent or sticky behavior belongs to the hardware registers named here. Some registers are writable policy/configuration registers that remain effective until reset, power transition, firmware reinitialization, link reset, function reset, or driver reprogramming. Others are hardware-updated status, error-log, performance-counter, strap-shadow, or write-one-to-clear style registers whose access rules are not encoded in this offset header.

## Dependencies And Integration Points

The direct include site in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. That implementation uses the generated register names with SOC15 helpers to initialize NBIO state, configure memory-controller access, doorbell apertures and ranges, interrupt handling, HDP flush offsets, PCIe index/data offsets, clock-gating policy, and PCIe master control. For this specific chunk, `nbio_v7_7_init_registers()` reads and conditionally writes `regBIF0_PCIE_MST_CTRL_3` using companion shift/mask fields.

The semantic dependencies are AMD's NBIO 7.7 register database, the SOC15 register addressing model, the PCI and PCI Express configuration-space specifications, root-port/link training semantics, PCIe AER, ACS, DPC, LTR, L1 PM substates, lane margining, high-speed equalization, CCIX/ESM capability layout, and AMD firmware/SMU ownership rules for selected NBIO and PCIe registers.

The companion `nbio_7_7_0_sh_mask.h` file is required when consumers need bitfield extraction or insertion. This offset header only identifies register addresses; it does not describe bit positions, masks, reset values, access widths, access permissions, side effects, or firmware arbitration.

## Risks And Maintenance Notes

- This is generated hardware ABI. Renaming a macro, changing an offset, or mixing it with a different NBIO generation can compile cleanly while targeting the wrong register.
- The chunk starts and ends mid-block. Adjacent chunks are required for a full per-file report and for complete `BIFP3_0` and `BIFPLR3_1` coverage.
- Repeated `BIFPLR0_1`, `BIFPLR1_1`, `BIFPLR2_1`, and `BIFPLR3_1` layouts are easy to confuse. Prefix mistakes can affect the wrong root port or link-root instance without producing a compiler error.
- Some symbolic registers intentionally share offsets because multiple PCI config fields occupy the same DWORD, for example `VENDOR_ID`/`DEVICE_ID`, `COMMAND`/`STATUS`, `LINK_CNTL`/`LINK_STATUS`, lane control/status pairs, and grouped per-lane equalization registers. Consumers must use the companion masks rather than assuming one macro means one independent storage location.
- Error injection, AER, DPC, reset, and local error registers can have destructive or sticky side effects on real hardware. Offset availability does not imply safe unconditional writes.
- Link speed, width, equalization, L1 substate, clock gating, and save/restore registers interact with live PCIe link training and platform power policy. Incorrect programming can cause link retraining, performance loss, hangs, or device disappearance.
- Strap and SMU/SMN-facing registers may reflect firmware-owned state. Driver writes must follow the sequencing and ownership rules in the NBIO implementation and platform firmware documentation.
- All macros use untyped preprocessor constants. There is no compile-time check that a register is accessed through the right aperture, with the right width, or under the right lock/clock/power condition.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage of `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` with this header and `nbio_7_7_0_sh_mask.h` included.
- Generated-header comparison against AMD's authoritative NBIO 7.7 register database, with special attention to the repeated port/root-port offsets and the mid-block chunk boundaries.
- Static checks that every non-`_BASE_IDX` macro in this range has a matching `*_BASE_IDX` macro and that all base indexes remain the expected SOC15 NBIO value.
- Cross-checks that bitfield references used with chunk registers, such as `BIF0_PCIE_MST_CTRL_3__*`, exist in the matching shift/mask header for the same ASIC generation.
- Hardware or simulator register-dump comparisons for NBIO 7.7 devices, especially PCIe port 3/4 link state, global `BIF0` PCIe control/status, and PCIe1 root-port config spaces for `BIFPLR0_1` through `BIFPLR3_1`.
- PCIe enumeration and `lspci -vvxxx` style validation for root-port identity, bridge windows, PCIe capabilities, AER, ACS, DPC, L1 PM substates, lane margining, and high-speed link capability/status fields.
- Runtime validation around `nbio_v7_7_init_registers()` that `regBIF0_PCIE_MST_CTRL_3` reads and writes the expected register and that master request-size behavior remains stable.
- Negative testing or guarded debug-only testing for error-injection, reset, and DPC paths, because those registers can intentionally perturb link or device state.

### subset-b-003253: lines 17060-19479

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 17060-19479

## Purpose

This chunk is an auto-generated AMD NBIO 7.7.0 register-offset slice for the second PCIe/NBIO instance. It exports preprocessor constants that map PCIe root-port configuration decode blocks and PCIe port-directory blocks to SOC15 register addresses. The macros are consumed by AMDGPU register helpers together with the companion shift/mask header; the header itself has no executable code.

The chunk starts in the middle of the `nbio_pcie1_bifplr3_cfgdecp` address block at `BIFPLR3_1_ROOT_CAP` and continues through the rest of that root-port configuration space. It then covers complete `BIFPLR4_1` and `BIFPLR5` root-port configuration decode blocks, complete `BIFP0_1` through `BIFP4_1` PCIe directory blocks, and the first four register entries in the `BIFP5` PCIe directory block.

## Public Surface In This Chunk

The exported API is 2,388 `#define` macros: 1,194 register-address macros plus 1,194 matching `*_BASE_IDX` macros. Every entry in this chunk uses base index `5`, which is the SOC15 NBIO register base selected by callers such as `SOC15_REG_OFFSET(NBIO, instance, reg...)`, `RREG32_SOC15`, `WREG32_SOC15`, and PCIe-port access helpers.

The named prefixes covered here are:

- `regBIFPLR3_1_*`: 464 macros for the tail of the root-port config block at `0x11203000`, beginning with PCIe root capability/status and continuing through extended PCIe capabilities.
- `regBIFPLR4_1_*`: 548 macros for the full root-port config block at `0x11204000`.
- `regBIFPLR5_*`: 548 macros for the full root-port config block at `0x11205000`.
- `regBIFP0_1_*` through `regBIFP4_1_*`: five repeated PCIe port-directory blocks at `0x11240000`, `0x11241000`, `0x11242000`, `0x11243000`, and `0x11244000`.
- `regBIFP5_*`: the first four PCIe port-directory offsets at `0x11245000`: reserved, scratch, port control, and TX requester ID.

There are no C types, functions, structs, or inline helpers in this range. Its stable interface is purely the generated macro naming convention and the address values encoded in those macros.

## Important Register Families

The `BIFPLR3_1` tail contains PCIe capability and extended-capability offsets for a root-port-like configuration space. It includes root capability/status; PCIe 2.0 device, link, and slot capability/control/status entries; MSI address/data and MSI mapping entries; SSID entries; vendor-specific enhanced capability entries; Virtual Channel capability/control/status and VC0/VC1 resource registers; Device Serial Number registers; Advanced Error Reporting status, masks, severities, control, header logs, root error command/status, error source ID, and TLP prefix logs; Secondary PCIe link-control and per-lane equalization entries for lanes 0-15; ACS capability/control; multicast capability/control/address/receive/block/overlay entries; L1 PM substate capability/control entries; DPC and RP PIO entries; ESM controls, capabilities, status, lane equalization at 16/20/25 GT, CCIX transition controls, and 32 GT link capability/control/status entries.

The `BIFPLR4_1` and `BIFPLR5` blocks repeat the full root-port configuration-space layout. They start with standard PCI header fields such as vendor/device ID, command/status, revision/class code, cache/latency/header/BIST, bus-number and bridge window registers, capability pointer, interrupt fields, and bridge control. They continue through PM capability, PCIe capability, device/link/slot/root capability and control registers, MSI/MSI-map/SSID, vendor-specific capability, VC resources, serial number, AER, secondary PCIe equalization, ACS, multicast, L1 PM substates, DPC/RP PIO, ESM, CCIX transition, and 32 GT link registers.

The `BIFP0_1` through `BIFP4_1` PCIe directory blocks expose port-facing link and data-link-layer controls rather than PCI config-space headers. Each block defines offsets for scratch and port control, TX requester ID, lane status, error control, RX control/expected sequence/vendor-specific/control3, RX credits for posted/non-posted/completion traffic, physical and transaction error injection, NAK counters, link-control and training registers, link-width and speed controls, link-state registers, bandwidth-change and CDR controls, lane controls, equalization coefficient controls, link-management masks, strap registers, L1 PM substate controls, BCH ECC control, fine-grain clock-gating override, save/restore registers, TX sequence/replay/ack-latency/credit threshold/vendor-specific/NOP/request-count controls, advertised and initial TX credits, credit status, and flow-control counters for posted, non-posted, and completion traffic on VC0 and VC1.

The `BIFP5` section is intentionally incomplete in this chunk. It begins the next PCIe port-directory block but stops at `regBIFP5_PCIE_TX_REQUESTER_ID`; the rest of that block is expected in the adjacent chunk.

## Control Flow And State

This header has no runtime control flow. The only "flow" is compile-time expansion:

1. A translation unit includes `nbio_7_7_0_offset.h` and usually `nbio_7_7_0_sh_mask.h`.
2. Driver code passes one of these `reg...` constants through AMDGPU/SOC15 register access macros.
3. The access helper combines the encoded offset and base index with the selected hardware instance and performs the actual MMIO, SMN, or PCIe-port-indexed read/write.

No state is stored in the header. Persistent state lives in the GPU hardware registers described by these constants. Writes through consumers can affect PCIe enumeration-visible config space, bridge windows, interrupt routing, link training and equalization, AER/DPC error reporting, ACS isolation, virtual-channel arbitration, multicast routing, L1 PM substates, ESM state, port error injection, credit accounting, and clock/power-related link controls.

Several macros intentionally share the same address where two PCIe fields occupy different halves of the same dword, for example device control/status, link control/status, slot control/status, MSI address/data overlays, ACS capability/control, and multicast capability/control. Correct users must pair these offset macros with the appropriate field masks from the shift/mask header instead of assuming one logical register per address.

## Dependencies And Integration Points

The direct C integration point for this specific generated header is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. That file uses the generated constants with `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and `REG_SET_FIELD` to implement NBIO v7.7 operations such as HDP flush remapping, revision ID extraction, memory-size reads, doorbell aperture setup, interrupt handling setup, PCIe index/data offset reporting, register initialization, clock gating, light sleep, and register remapping.

The companion `nbio_7_7_0_sh_mask.h` supplies field-level masks and shifts for the same register names. Reset/default information for corresponding NBIO register families is present in generated default headers such as `nbio_7_0_default.h`, including entries for `BIFPLR4_1`, `BIFPLR5`, and repeated `BIFP*` blocks. Semantic interpretation depends on AMD's NBIO 7.7.0 hardware spec and PCI/PCIe capability specifications for root ports, MSI, PM, PCIe extended capabilities, AER, VC, ACS, multicast, L1 PM substates, DPC, RP PIO, equalization, ESM, CCIX, and high-speed link controls.

## Risks And Maintenance Notes

- This is generated hardware contract data. Any wrong offset or base index can make otherwise correct driver code read or write the wrong NBIO register.
- The chunk boundaries are partial: it starts after the beginning of `BIFPLR3_1` and ends near the start of `BIFP5`. Adjacent chunk research is required for complete per-block coverage.
- The repetition across `BIFPLR4_1`, `BIFPLR5`, and `BIFP0_1` through `BIFP4_1` makes generation drift hard to review manually; a single dropped or shifted entry could be hidden among mostly identical names.
- Shared-address aliases are expected in PCIe config-space layouts. Callers that read-modify-write without the correct field mask can corrupt sibling fields in the same dword.
- Many target registers have hardware side effects or policy impact outside this header: AER and DPC status may be write-one-to-clear, error-injection registers can deliberately poison link behavior, link training/equalization controls can destabilize PCIe connectivity, ACS and bridge-window fields affect isolation and routing, and MSI/MSI-map fields affect interrupt delivery.
- These offsets are version-specific. Similar NBIO generations can use different address encodings or larger addresses, so these macros should not be reused for non-7.7.0 ASICs without the matching generated header.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` and any configuration that includes `nbio_7_7_0_offset.h` with `nbio_7_7_0_sh_mask.h`.
- Static generation checks that every non-`*_BASE_IDX` register macro in lines 17060-19479 has exactly one matching `*_BASE_IDX` macro and that all base indices remain `5`.
- Cross-header checks that register names in this offset slice have matching shift/mask definitions where fields are decoded or updated, and matching generated defaults where reset values are modeled.
- Hardware smoke tests on an NBIO 7.7.0 ASIC that compare decoded root-port config space and PCIe port-directory dumps against `lspci -vvxxx`, debugfs/MMIO register dumps, or firmware-provided register tables.
- Runtime tests around PCIe link speed/width reporting, retraining, equalization state, AER/DPC logging and clearing, MSI delivery, bridge-window programming, ACS isolation behavior, L1 PM substate transitions, and port credit/status counters.
- Negative tests should avoid writing error-injection, link-control, DPC, ACS, and bridge-routing registers on production hardware unless the test harness can recover the link and restore the device cleanly.

### subset-b-003254: lines 19480-21933

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 19480-21933

## Scope

This chunk is a generated AMDGPU NBIO 7.7 register-offset header segment. It contains 2,362 `#define` lines: 1,181 register-address macros and 1,181 matching `_BASE_IDX` macros. There are no functions, structs, enums, variables, locks, allocations, or executable statements in this range.

The range starts in the tail of a `BIFP5` PCIe port block, then covers several NBIO/IOHUB address blocks, NBIF0 BIF/RCC/GDC register windows, and ends in `BIFPLR0_2` PCIe capability/config-space aliases through lane 15 equalization control. Adjacent chunks are required for the beginning of the `BIFP5` block before line 19480 and any `BIFPLR0_2` registers that follow line 21933.

## Purpose

`nbio_7_7_0_offset.h` is the address half of AMD's generated NBIO 7.7 register interface. Each `reg*` macro gives a hardware register offset or encoded address, and each `<register>_BASE_IDX` macro tells AMDGPU's SOC15 register helpers which NBIO base index to use. In this chunk every visible `_BASE_IDX` value is `5`.

This segment maps low-level PCIe, NBIO, IOMMU L2A, BIF, RCC, GDC, RAS, trap, doorbell, mailbox, MSI-X, and PCIe config/capability registers. The constants let runtime driver code use named hardware registers through helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT` instead of hard-coded offsets.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware metadata and has no direct Ceph or distributed-filesystem behavior.

## Register Families

The opening `BIFP5` tail covers PCIe protocol/link registers for an existing port block: TX skid, lane status, error control, RX sequence/vendor/credit state, physical and transaction error injection, NAK/LTR/AER controls, link-control state registers, link-width/speed/equalization controls, L1 PM substate registers, BCH ECC/HPGI/performance controls, save/restore slots, TX sequence/replay/credit/flow-control registers, and VC0/VC1 flow-control counters.

The `nbio_pcie1_pciedir` block starts `BIF1` PCIe port registers at base address `0x11280000`. It includes common PCIe control/status, RX last-TLP capture, I2C expansion/data access, link power-management controls, physical-port status, SDP and CLKREQ mapping, performance counters, strap registers, PRBS clear/status/free-run/pattern/error counters for lanes 0 through 15, software reset command/control registers, power-gating master/slave controls, RX margining, presence detect, LC debug, TX last-TLP capture, tracking registers, TX status/attribute controls, bandwidth and master controls, and HIP registers.

The `nbio_iohub_nb_nbcfg_nb_cfgdec`, `fastreg`, `misc`, and `rascfg` blocks expose IOHUB/NB configuration space. They include NB vendor/device/command/status/class/cache/header/capability aliases, SMN index/data windows, scratch registers, DRAM aperture and top-of-memory registers, interrupt-routing and parity controls, MMIO CAM target/remap entries, dropped DMA logs, VDM controls, xbar stall controls, SMU and fastreg base addresses, trap request/response registers, 16 repeated trap match units, RAS action-control registers for PCIE0 ports A-F and NBIF1 ports A-C, sync flood/NMI/poison status and masks, and APML status/control/trigger registers.

The IOMMU `l2acfg` block maps L2A performance counters, status/control registers, DTC/ITC/PTC hash and way controls, credit controls, update filters, error-rule controls, clock/power/page-size controls, memory power gates, power-gate control, and ECO control. The adjacent `l2ashdw` block is present as an address-block marker in this range but has no register macros inside the chunk.

The NBIF0 BIF/RCC/GDC portion maps indirect MMIO and PCIe index/data windows, SBIOS/BIOS scratch registers, BIF interrupt controls, GFX MMIO CAM remaps, RCC strap registers, RCC endpoint/downstream/downstream-port registers, EPF0 VF/PF aperture controls, MSI/MSI-X table entries, requester/device/function restore, LTR and arbitration controls, BIF bus/reset/doorbell/FB enable controls, GPU-I/O virtualization aperture sizes, HDP coherency flush/invalidate controls, transaction-pending status, VM/HV mailbox buffers, GDC SDP/clock/power controls, and doorbell ranges for SDMA, IH, VCN, RLC, CSDMA, and related clients.

The final high-address `nbio_iohub_nb_nbcfg_nb_cfgdec` and `nbio_pcie0_bifplr0_cfgdecp` blocks expose large encoded config-space aliases. `NB_NBCFG1` repeats northbridge PCI configuration/header, SMN index/data, scratch, DRAM, and mutex registers. `BIFPLR0_2` maps PCI header fields, PM/PCIe/MSI/SSID/MSI-map capabilities, PCIe vendor-specific and virtual-channel enhanced capabilities, device serial number, AER status/masks/severity/header/TLP-prefix logs, root error command/status/source ID, secondary PCIe capability, link control 3, lane error status, and lane 0-15 equalization controls.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor namespace:

- `reg<name>` macros are integer constants used as register selectors.
- `reg<name>_BASE_IDX` macros select the SOC15 base index for those registers.

The offsets do not encode bit fields, reset values, access permissions, write-one-to-clear behavior, ordering requirements, ownership, or side effects. Consumers must pair these macros with `nbio_7_7_0_sh_mask.h` for field layout, any generated default metadata for reset values, and AMDGPU's register access helpers for the correct access path.

## Control Flow

This header has no local runtime control flow. Runtime flow is external:

1. NBIO 7.7 driver code includes `nbio_7_7_0_offset.h` and the matching shift/mask header.
2. Code passes a `reg*` macro through `SOC15_REG_OFFSET(NBIO, instance, reg)` or a PCIe-port accessor helper.
3. The read or write reaches the selected NBIO, PCIe, RCC, GDC, RAS, IOMMU, or config-space register.
4. Field operations use the companion shift/mask macros to preserve unrelated bits while programming the register.

The main visible consumer is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes this header and uses this generated register namespace for NBIO 7.7 operations such as HDP flush register remapping, PCIe index/data offset reporting, doorbell aperture setup, interrupt handler dummy-read control, memory controller access enablement, clock gating/light sleep, and initialization workarounds.

## State And Persistence Behavior

The header owns no software state and persists nothing. It describes hardware-visible register locations whose state lives in GPU/NBIO reset and power domains.

Represented state includes PCIe link/protocol state, AER and RAS status/action controls, PRBS diagnostic counters, RX margining controls, software reset controls, interrupt routing, memory aperture and remap registers, HDP flush/invalidate requests and completion status, doorbell aperture/range programming, GPU virtualization and mailbox registers, trap comparators, poison/NMI/sync-flood status, IOMMU L2A performance and power controls, PCIe capability/configuration aliases, and MSI/MSI-X table entries.

Persistence depends on the specific register's reset domain, PCIe reset, GPU reset, BACO/power-gating state, firmware/BIOS programming, SR-IOV PF/VF ownership, suspend/resume restore, and explicit driver writes. Register-address macros alone must not be treated as evidence that a value survives reset or is safe to cache.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.7 register database and must remain synchronized with sibling generated headers:

- `nbio_7_7_0_sh_mask.h` provides bit shifts and masks for the same register names.
- Other generated NBIO 7.7 metadata provides defaults or additional address views where present.
- AMDGPU SOC15 and PCIe-port accessors interpret the offset and base-index macros.

Important integration points include:

- `amdgpu/nbio_v7_7.c`, which binds these constants into `nbio_v7_7_funcs` and `nbio_v7_7_hdp_flush_reg`.
- `amdgpu_discovery.c`, which selects NBIO 7.7 functions for discovered hardware.
- Doorbell, HDP, IH, SDMA, VCN, RLC, KFD, SR-IOV, PCIe link-management, RAS, and power-management paths that rely on correct NBIO register addresses.

## Risks And Edge Cases

- Generated offset drift can compile cleanly while redirecting reads or writes to the wrong hardware register, causing PCIe link failures, broken doorbells, missed interrupts, invalid HDP flush completion checks, RAS misrouting, or GPU reset/resume regressions.
- The chunk starts mid-`BIFP5` block and ends in the `BIFPLR0_2` capability block. Whole-file research must reconcile neighboring chunks before treating either family as complete.
- Several address blocks share the same base address `0xd0000000` but represent different decoders. Consumers must use the intended macro namespace and access path, not just compare raw values.
- The high encoded addresses such as `0x3fff7bfc...` are config-space aliases, not ordinary small MMIO offsets. Truncation, sign extension, or using a 32-bit-only path incorrectly would be dangerous.
- Trap, reset, poison, RAS action-control, AER, error-injection, and PRBS registers have diagnostic or fault-routing side effects. Accidental writes can mask hardware errors, inject faults, reset blocks, or perturb link diagnostics.
- Doorbell aperture/range and mailbox registers interact with queue submission, virtualization, KFD, and host memory visibility. Incorrect programming can break command submission or isolate the wrong client.
- Scratch, strap, BIOS/SBIOS, requester-ID restore, and PCIe capability aliases may be firmware-owned or boot-time sampled. Runtime writes need hardware documentation and sequencing.
- Repeated lane, port, trap, and action-control macro families are mechanically generated; lane or port off-by-one mistakes are plausible at call sites because many names and offsets differ only by a number.

## Test Signals

- Build AMDGPU with NBIO 7.7 support enabled. Compile-time coverage catches missing or renamed generated symbols used by `nbio_v7_7.c` and related code.
- Run generated-header consistency checks: every `reg*` macro in this chunk should have a matching `_BASE_IDX`, base-index values should match the SOC15 NBIO instance mapping, and duplicated config aliases should intentionally share offsets.
- Cross-check `nbio_7_7_0_offset.h` against `nbio_7_7_0_sh_mask.h` so field macros exist for registers that runtime code reads or writes.
- On supported hardware, validate PCIe link bring-up/retraining, link-speed/width reporting, RX margining visibility, PRBS diagnostics, suspend/resume, BACO or GPU reset recovery, and clock-gating/light-sleep transitions.
- Exercise HDP flush/invalidate paths, doorbell ranges for SDMA/IH/VCN/RLC/CSDMA, interrupt handling, KFD remapped HDP registers, and SR-IOV PF/VF register access where applicable.
- Validate RAS and AER behavior by checking that correct status, mask, severity, root error, poison, NMI, sync-flood, and action-control registers are read or written for each port.
- Review register traces for writes to reset, trap, error-injection, PRBS, RAS, and strap/config aliases to ensure they are intentional, sequenced, and use read-modify-write with the companion masks where fields share registers.

### subset-b-003255: lines 21934-24299

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 21934-24299

## Purpose

This chunk is an auto-generated AMD NBIO 7.7.0 register offset-header slice for PCIe bridge/root-port configuration decode windows. It contains only C preprocessor constants: register-address macros and matching `_BASE_IDX` macros. There are no executable functions, structs, enums, variables, locks, allocations, or algorithms in this range.

The assigned lines start in the tail of the `nbio_pcie0_bifplr0_cfgdecp` address block, cover complete `nbio_pcie0_bifplr1_cfgdecp` through `nbio_pcie0_bifplr4_cfgdecp` blocks, cover narrow partial `nbio_pcie1_bifplr0_cfgdecp` through `nbio_pcie1_bifplr4_cfgdecp` bridge-window/slot/subsystem blocks, cover a larger `nbio_pcie1_bifplr5_cfgdecp` block, and then enter `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` through `BIF_CFG_DEV0_RC1_PCIE_VENDOR_SPECIFIC_ENH_CAP_LIST`.

The offsets name NBIO-backed PCI/PCIe configuration-space registers for root-port/bridge-like functions. Driver code combines these constants with `nbio_7_7_0_sh_mask.h` field definitions and AMDGPU register helpers to read, write, or form SOC15 register offsets without embedding raw addresses.

## Public Surface

The public surface in this range is 2,322 macros: 1,161 register-address macros and 1,161 matching `_BASE_IDX` macros. Every `_BASE_IDX` macro in the chunk has value `5`, selecting the NBIO SOC15 base slot used by AMDGPU register-access helpers.

The key macro families are:

- `regBIFPLR0_2_*`: tail of PCIe controller 0 root-port 0, beginning at ACS/multicast/L1 PM/DPC/ESM/link-speed extended capabilities and ending at 32 GT/s link status.
- `regBIFPLR1_2_*` through `regBIFPLR4_2_*`: complete PCIe controller 0 root-port blocks from conventional PCI identity/header registers through 32 GT/s link registers.
- `regBIFPLR0_3_*` through `regBIFPLR4_3_*`: partial PCIe controller 1 root-port blocks containing bridge bus/window registers, slot capability/control/status, slot capability 2/control 2/status 2, and subsystem ID capability addresses.
- `regBIFPLR5_1_*`: a larger PCIe controller 1 root-port block from conventional PCI identity/header registers through Gen5/CCIX/ESM/32 GT/s link registers.
- `regBIF_CFG_DEV0_RC1_*`: start of the NBIF root-complex configuration block from vendor/device ID through MSI, subsystem/MSI-map, and the first vendor-specific enhanced capability address.

Address-block comments identify these bases inside the range: `nbio_pcie0_bifplr1_cfgdecp` at `0xfffe0000a000`, `bifplr2` at `0xfffe0000b000`, `bifplr3` at `0xfffe0000c000`, `bifplr4` at `0xfffe0000d000`, PCIe1 `bifplr0` through `bifplr5` at `0xfffe00011000` through `0xfffe00016000`, and `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp` at `0xfffe00041000`. The initial `BIFPLR0_2` tail belongs to the earlier `nbio_pcie0_bifplr0_cfgdecp` block whose marker and base `0xfffe00009000` appear before this chunk.

## Register Coverage

The `BIFPLR0_2` tail covers PCIe extended capability address constants for access control services, multicast, L1 PM substates, downstream port containment, root-port PIO status/mask/severity/sys-error/exception and logs, ESM capability/status/control/capability registers, and 16 GT/s plus 32 GT/s link capability/control/status registers. This chunk does not include the conventional PCI/PCIe header for `BIFPLR0_2`; that context is in the previous chunk.

The full `BIFPLR1_2` through `BIFPLR4_2` blocks repeat a root-port style PCI configuration layout:

- Conventional PCI bridge fields: vendor/device ID, command/status, revision and class-code bytes, cache-line/latency/header/BIST, subordinate bus and latency register, I/O/memory/prefetchable bridge windows, capability pointer, interrupt line/pin, and bridge control.
- Power-management and PCIe capability fields: PM capability/status-control, PCIe capability header, device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, and PCIe capability 2 device/link/slot controls and statuses.
- Interrupt and identification fields: MSI capability list/control/address/data forms, SSID capability, and MSI-map capability.
- Extended capabilities: vendor-specific enhanced capability, virtual-channel capability/control/status/resource groups for VC0 and VC1, device serial number, Advanced Error Reporting, TLP header/prefix logs, secondary PCIe link control/lane error/equalization controls, ACS, multicast, L1 PM substates, DPC, RP PIO diagnostics, ESM, and 16 GT/s/32 GT/s link-speed capability groups.

The partial `BIFPLR0_3` through `BIFPLR4_3` ranges are intentionally narrow. For each of these five PCIe1 root-port instances, this chunk defines only `SUB_BUS_NUMBER_LATENCY`, I/O/memory/prefetchable window registers, `SLOT_CAP`, `SLOT_CNTL`, `SLOT_STATUS`, `SLOT_CAP2`, `SLOT_CNTL2`, `SLOT_STATUS2`, `SSID_CAP_LIST`, and `SSID_CAP`. The rest of each `_3` block is outside this range and must be reconciled with adjacent chunks.

The `BIFPLR5_1` block is the broadest block in this chunk. In addition to the standard bridge, PM, PCIe, MSI, SSID, MSI-map, VSEC, VC, serial-number, AER, secondary PCIe, ACS, multicast, L1 PM, DPC, RP PIO, ESM, and 16/32 GT/s groups, it includes address constants for data-link feature capability/status, PCIe PHY 16 GT/s parity mismatch status, Gen4 lane equalization controls, PCIe lane-margining control/status registers for lanes 0-15, CCIX capability/ESM registers, ESM lane equalization controls for 20 GT/s and 25 GT/s, and CCIX translation capability/control registers.

The final `BIF_CFG_DEV0_RC1` portion starts another address block for the NBIF root-complex configuration function. It covers identity/header fields, BARs, bridge windows, ROM BAR, interrupt/bridge controls, PM and PCIe capabilities, PCIe device/link/slot/root capability groups, MSI address/data forms including extended message data, SSID/MSI-map fields, and stops at the vendor-specific enhanced capability list. The vendor-specific header and later extended capabilities continue after this chunk.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A translation unit includes `nbio/nbio_7_7_0_offset.h` and usually `nbio/nbio_7_7_0_sh_mask.h`.
2. Code selects a register address macro, for example a `regBIFPLR*_2_*`, `regBIFPLR*_3_*`, `regBIFPLR5_1_*`, or `regBIF_CFG_DEV0_RC1_*` name.
3. `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, or related AMDGPU helpers combine the macro with NBIO instance/base information.
4. Field extraction or updates use sibling shift/mask macros from `nbio_7_7_0_sh_mask.h` or PCIe config-space conventions.

The header stores no software state and persists nothing. State lives in hardware PCIe/NBIO configuration registers and may be affected by reset, FLR, link retraining, power transitions, firmware policy, platform PCI enumeration, hotplug, or explicit driver writes. Some addressed registers are read-only identity/status, some are writable policy/control, and some are sticky error/log registers. The offset header does not encode access permissions, reset values, side effects, or write-one-to-clear behavior.

## Dependencies And Integration Points

The direct NBIO 7.7 include site in this tree is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h`. That implementation uses the same generated-header pattern for NBIO register access through `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `REG_SET_FIELD`, and `REG_GET_FIELD` style helpers. The exact root-port macros in this chunk are mostly a generated hardware map rather than frequently hand-referenced C symbols, but they remain part of the address namespace available to NBIO, PCIe, diagnostics, and generated access code.

The critical dependency is the sibling `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h` header. Offset macros identify where a register lives; shift/mask macros identify how fields are packed. Mixing this NBIO 7.7.0 offset header with another ASIC generation's shift/mask header can compile while silently targeting the wrong register or field.

Semantic dependencies include the PCI and PCI Express configuration-space layouts, PCIe bridge/window semantics, MSI, subsystem ID, vendor-specific enhanced capabilities, Virtual Channel, Device Serial Number, Advanced Error Reporting, Secondary PCIe capability, ACS, Multicast, L1 PM Substates, Downstream Port Containment, RP PIO logging, ESM, Data Link Feature, PCIe 4.0/5.0 link equalization and lane margining, and CCIX-related extended capability conventions.

## Risks And Maintenance Notes

- The chunk boundaries split several address blocks. `BIFPLR0_2` starts mid-block, each `BIFPLR*_3` slice is partial, and `BIF_CFG_DEV0_RC1` stops just after the vendor-specific enhanced capability list. Whole-file research must merge adjacent chunks before claiming complete coverage of those blocks.
- The repeated `BIFPLR1_2` through `BIFPLR4_2` templates invite prefix mistakes. A register name with the wrong root-port prefix can compile cleanly while addressing a different port.
- Some different logical register names intentionally share the same dword address, such as command/status, device control/status, link control/status, capability/control pairs, and lane groups that pack multiple lanes per dword. Consumers must use the right field masks and access width rather than treating each macro as a unique physical word.
- All `_BASE_IDX` values are `5`; changing the base index or mixing helper paths would redirect accesses away from the intended NBIO aperture.
- AER, DPC, RP PIO, ESM, and TLP log registers are error-handling surfaces. Incorrect offsets can hide, misclassify, or clear PCIe faults.
- Bridge bus/window and slot-control offsets affect PCI topology visibility, hotplug state, and bridge aperture programming. These should normally be coordinated with PCI core and firmware policy rather than updated casually from device-driver code.
- Gen4/Gen5 link equalization, lane margining, DLF, and CCIX/ESM controls are hardware- and platform-sensitive. Writes using these offsets can affect link stability and interoperability.
- Generated headers provide no type safety, locking model, or ordering guarantees. Callers must supply the access sequencing, posting reads, reset handling, and firmware ownership checks where needed.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for AMDGPU NBIO 7.7 users, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, with `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h` included together.
- Generated-header consistency checks that every address macro in this range has a matching `_BASE_IDX` macro with value `5`, and that each address macro has compatible field definitions in `nbio_7_7_0_sh_mask.h`.
- Address-block checks that repeated `BIFPLR1_2` through `BIFPLR4_2` layouts are structurally aligned, while documented exceptions for `BIFPLR0_2`, `BIFPLR*_3`, `BIFPLR5_1`, and `BIF_CFG_DEV0_RC1` are preserved.
- Hardware or simulator PCI config-space dumps for the corresponding root ports/root-complex function, compared against these offsets and standard `lspci -vvxxx` decoding for PCIe capabilities, MSI, VC, AER, ACS, DPC, L1 PM, link-speed, and lane-margining registers.
- Error-injection or fault-observation tests that verify AER/DPC/RP PIO/ESM status, masks, source IDs, header logs, and prefix logs decode at the expected addresses.
- Link training and margining tests on supported hardware that confirm 16 GT/s and 32 GT/s capability/control/status addresses line up with observed negotiated speed, lane width, equalization, and margining state.
- Static checks that no hand-written code pairs an offset from this NBIO 7.7.0 header with a field mask from another NBIO generation.

### subset-b-003256: lines 24300-26645

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 24300-26645

## Purpose

This chunk is an auto-generated AMD NBIO 7.7.0 register-offset slice for PCI/PCIe configuration-space registers exposed through NBIO BIF configuration decode blocks. It contains no executable code. Its job is to publish preprocessor constants that map AMDGPU register names to NBIO register addresses and base-index selectors for root-complex ports and endpoint functions.

The selected range begins in the middle of the `DEV0_RC1` root-complex block at PCIe vendor-specific and virtual-channel registers, then covers complete `DEV1_RC1` and `DEV2_RC1` root-complex blocks. It also covers complete `DEV0_EPF0_1` and `DEV0_EPF1_1` endpoint-function blocks, and ends in the early portion of the `DEV0_EPF2_1` block at `PCIE_VENDOR_SPECIFIC1`. Adjacent chunks are required for the beginning of `DEV0_RC1` and the remainder of `DEV0_EPF2_1`.

## Public Surface In This Chunk

The public surface is 2,326 `#define` macros in the assigned range: 1,163 register-address macros and 1,163 matching `_BASE_IDX` macros. Every register address macro in this chunk has a companion base-index macro with value `5`, which tells the AMDGPU register helpers which SOC15/NBIO base aperture to use when resolving the generated address.

Macro prefixes identify the logical PCI function or port:

- `regBIF_CFG_DEV0_RC1_*` covers the tail of the first root-complex block in this range.
- `regBIF_CFG_DEV1_RC1_*` and `regBIF_CFG_DEV2_RC1_*` cover two complete root-complex PCI/PCIe configuration maps.
- `regBIF_CFG_DEV0_EPF0_1_*`, `regBIF_CFG_DEV0_EPF1_1_*`, and `regBIF_CFG_DEV0_EPF2_1_*` cover endpoint-function configuration maps under device 0.

There are no functions, structs, enums, storage objects, or inline helpers. The API contract is the exact macro spelling and numeric value. Consumers are expected to pair these offsets with field definitions from `nbio_7_7_0_sh_mask.h` and with AMDGPU's generated-register access helpers.

## Register Coverage

The chunk has five explicit address-block markers:

- `nbio_nbif0_bif_cfg_dev1_rc_bifcfgdecp`, base address `0xfffe00042000`, with 185 register offsets from `regBIF_CFG_DEV1_RC1_VENDOR_ID` through `regBIF_CFG_DEV1_RC1_LANE_15_MARGINING_LANE_STATUS`.
- `nbio_nbif0_bif_cfg_dev2_rc_bifcfgdecp`, base address `0xfffe00043000`, with 185 register offsets from `regBIF_CFG_DEV2_RC1_VENDOR_ID` through `regBIF_CFG_DEV2_RC1_LANE_15_MARGINING_LANE_STATUS`.
- `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, base address `0xfffe12100000`, with 348 register offsets from `regBIF_CFG_DEV0_EPF0_1_VENDOR_ID` through `regBIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_UVD1SCH_DW8`.
- `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`, base address `0xfffe12101000`, with 256 register offsets from `regBIF_CFG_DEV0_EPF1_1_VENDOR_ID` through `regBIF_CFG_DEV0_EPF1_1_PCIE_VF_RESIZE_BAR6_CNTL`.
- `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp`, base address `0xfffe12102000`, beginning here with 71 register offsets from `regBIF_CFG_DEV0_EPF2_1_VENDOR_ID` through `regBIF_CFG_DEV0_EPF2_1_PCIE_VENDOR_SPECIFIC1`.

The chunk also includes 118 tail offsets for `DEV0_RC1`, starting at `regBIF_CFG_DEV0_RC1_PCIE_VENDOR_SPECIFIC_HDR` and ending at `regBIF_CFG_DEV0_RC1_LANE_15_MARGINING_LANE_STATUS`. That root-complex block begins before this chunk, so identity, bridge-window, MSI, SSID, and MSI-map definitions for `DEV0_RC1` are only visible in the previous range.

Root-complex coverage includes conventional PCI header fields, bridge-window registers, bridge interrupt/control registers, power-management capability registers, PCIe capability and link registers, MSI and SSID/MSI-map capability offsets, vendor-specific extended capability offsets, virtual-channel resources, device serial number, Advanced Error Reporting, secondary PCIe capability, lane equalization, Access Control Services, Data Link Feature capability, 16 GT/s PHY capability, and PCIe lane margining registers.

Endpoint-function coverage includes conventional PCI header fields, BAR registers, capability pointer and interrupt bytes, vendor/adapter capability offsets, power-management capability offsets, SBRN/FLADJ/DBESL, PCIe device/link capability and control/status registers, MSI/MSI-X capability offsets, SATA capability/index/data offsets, vendor-specific extended capability offsets, Advanced Error Reporting and TLP logs, BAR enhanced capability offsets, SR-IOV capability and VF BAR controls, Address Translation Service and Page Request Interface registers, Process Address Space ID capability/control, data-link and 16 GT/s PHY capability registers, lane margining controls/statuses, and resizable VF BAR capabilities. `EPF0` additionally exposes a large GPU I/O virtualization vendor-specific register area, including VF framebuffer base/limit, device ID, FLR, doorbell, MMIO, and scheduling dword registers.

## Important Macro Patterns

Many macro names intentionally alias the same register dword because PCI configuration space packs multiple fields into one address. Examples include `VENDOR_ID` and `DEVICE_ID` sharing offset `...0000`, `COMMAND` and `STATUS` sharing `...0001`, class-code bytes sharing `...0002`, and interrupt/min-grant/max-latency fields sharing `...000f` in endpoint blocks. Similar aliases appear for `DEVICE_CNTL`/`DEVICE_STATUS`, `LINK_CNTL`/`LINK_STATUS`, `MSI_CAP_LIST`/`MSI_MSG_CNTL`, MSI 32-bit versus 64-bit data/mask/pending forms, `MSIX_CAP_LIST`/`MSIX_MSG_CNTL`, and lane control/status pairs.

The root-complex blocks use address ranges beginning with `0x3fff7bfd...`, while endpoint-function blocks use `0x3fff8080...`. The `_BASE_IDX` value remains `5` across all macros, so the changing high address bits and generated names are the main distinction between ports/functions within this chunk.

## Control Flow And State

There is no runtime control flow in this header. The effective flow is compile-time substitution:

1. A translation unit includes `nbio/nbio_7_7_0_offset.h`, usually with `nbio/nbio_7_7_0_sh_mask.h`.
2. Driver code chooses an offset macro such as `regBIF_CFG_DEV0_EPF0_1_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_VF0_FB`.
3. AMDGPU register helpers combine the generated register offset, the `_BASE_IDX` selector, and any shift/mask constants from the companion header.
4. Actual reads, writes, polling, error handling, or capability programming happen in AMDGPU NBIO, PCIe, RAS, interrupt, virtualization, or power-management code outside this generated header.

The header stores no software state and persists nothing by itself. Persistent state lives in hardware registers, PCI/PCIe configuration space, firmware-managed NBIO state, or platform PCI enumeration state. Some registers are writable controls that persist until reset, FLR, link reset, power transition, or driver reinitialization. Others are hardware-updated status, sticky error, log, or write-one-to-clear registers whose side effects are defined by PCIe and AMD hardware documentation, not by this offset header.

## Dependencies And Integration Points

The primary direct integration point is `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes both `nbio_7_7_0_offset.h` and `nbio_7_7_0_sh_mask.h` and provides the `nbio_v7_7_funcs` implementation. That implementation wires NBIO register access into AMDGPU through callbacks for HDP flush offsets, PCIe index/data offsets, PCIe port index/data offsets, revision ID, memory-controller access, doorbell apertures, interrupt-handler doorbell ranges, clock gating, light sleep, initialization, HDP register remapping, and register remap setup.

`drivers/gpu/drm/amd/amdgpu/nbio_v7_7.h` exports `nbio_v7_7_hdp_flush_reg`, `nbio_v7_7_funcs`, and `nbio_v7_7_ras_funcs`. `drivers/gpu/drm/amd/amdgpu/amdgpu_discovery.c` selects these NBIO 7.7 functions for matching discovered IP versions. The generated constants in this chunk are therefore part of the hardware contract used after ASIC discovery chooses the NBIO 7.7 backend.

Semantic dependencies include the PCI and PCI Express configuration-space specifications, MSI/MSI-X, AER, ACS, ATS, PRI, PASID, SR-IOV, resizable BAR, PCIe 16 GT/s equalization and lane margining, and AMD's NBIO 7.7.0 register database. The header does not encode reset values, access permissions, ownership rules, firmware arbitration, register-lock sequencing, or whether every register is valid on every NBIO 7.7 ASIC.

## Risks And Maintenance Notes

- This range is chunked across logical blocks. `DEV0_RC1` starts before this range, and `DEV0_EPF2_1` continues after it, so isolated analysis must not treat either as complete.
- Repetition across `DEV1_RC1`, `DEV2_RC1`, `EPF0`, `EPF1`, and `EPF2` makes prefix mistakes the main practical risk. A wrong `DEV*` or `EPF*` macro can compile cleanly while targeting a different PCI function or port.
- Overlapping address aliases are intentional. Consumers must use companion shift/mask definitions to access the intended field and must not assume each macro names a distinct dword.
- Root-complex AER, ACS, virtual-channel, link equalization, 16 GT/s, and lane-margining offsets are hardware-control and diagnostics surfaces. Incorrect writes can hide PCIe errors, alter link training behavior, or disrupt link health reporting.
- Endpoint MSI/MSI-X and SR-IOV offsets are virtualization-sensitive. Misprogramming can affect interrupt delivery, VF BAR layout, VF enumeration, FLR handling, doorbells, MMIO aperture exposure, and GPU I/O virtualization scheduling state.
- ATS, PRI, and PASID offsets interact with IOMMU and process-address-space policy. Enabling or decoding them incorrectly can affect translation, isolation, and page-request behavior.
- GPUIOV vendor-specific offsets in `EPF0` are AMD-specific and not self-describing. They should be modified only by code paths that understand firmware and virtualization ownership.
- Generated addresses and `_BASE_IDX` values must remain synchronized with `nbio_7_7_0_sh_mask.h` and the upstream register database; hand edits are high risk.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for NBIO 7.7 include sites, especially `amdgpu/nbio_v7_7.c` and discovery paths that select `nbio_v7_7_funcs`.
- Generated-header comparison against AMD's authoritative NBIO 7.7.0 register database, with special attention to the repeated `DEV1_RC1`/`DEV2_RC1` and `EPF0`/`EPF1`/`EPF2` blocks.
- Cross-header checks that every register in this chunk has a matching `_BASE_IDX` and compatible field definitions in `nbio_7_7_0_sh_mask.h`.
- Static checks that duplicated numeric offsets are expected PCI config aliases rather than accidental copy/paste errors.
- Hardware or simulator PCI config-space dumps compared against the generated offsets for root-complex ports and endpoint functions.
- PCIe link validation around AER, ACS, equalization, 16 GT/s capability, and lane margining registers.
- SR-IOV and GPU I/O virtualization tests that enumerate VFs, exercise FLR, verify VF BAR and resizable VF BAR state, validate GPUIOV framebuffer/doorbell/MMIO registers, and confirm MSI/MSI-X delivery remains stable.
- IOMMU-backed virtualization tests for ATS, PRI, and PASID enablement and teardown, including reset and power-transition coverage.

### subset-b-003257: lines 26646-29000

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 26646-29000

## Scope

This chunk is part of the generated AMDGPU NBIO 7.7.0 register offset header. It covers a PCIe configuration-space macro range from `regBIF_CFG_DEV0_EPF2_1_PCIE_VENDOR_SPECIFIC2` at line 26646 through `regBIF_CFG_DEV2_EPF0_1_PCIE_LANE_7_EQUALIZATION_CNTL` at line 29000. The chunk contains 2,323 `#define` entries: 1,162 register-name aliases and 1,161 matching `*_BASE_IDX` entries. The one-count difference is caused by the chunk ending on a register alias whose `*_BASE_IDX` line appears after the chunk boundary.

The chunk is source-tree-aligned with NBIO register descriptions, not with executable C logic. It is consumed by AMDGPU NBIO code through SOC15 register access macros after inclusion from `drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`.

## Purpose

The purpose of this header segment is to publish stable symbolic names for NBIO 7.7.0 PCIe BIF configuration registers. These symbols let driver code refer to GPU PCIe endpoint, root-complex, and function-specific configuration registers by semantic names instead of raw encoded offsets.

This chunk is dominated by endpoint-function config blocks:

- Tail of `DEV0_EPF2`, from PCIe vendor-specific enhanced capability through AER, BAR, power-budget, DPA, ACS, PASID, and ARI registers.
- Full `DEV0_EPF3` through `DEV0_EPF7` blocks, each with conventional PCI config header registers, power management, PCIe capability, MSI/MSI-X, SATA/vendor-specific capability registers, AER, BAR enhanced capability, power-budget, DPA, ACS, PASID, and ARI entries.
- Full `DEV1_EPF0`, a larger function block that includes the common endpoint register set plus VC/resource capabilities, secondary PCIe capability, lane equalization controls, 16 GT/s PHY capability/status, and lane margining controls.
- Full `DEV1_EPF1`, a shorter endpoint-function block similar to the DEV0 EPF3-EPF7 pattern.
- Start of `DEV2_EPF0`, including standard config header, power management, PCIe, MSI/MSI-X, vendor-specific and VC capabilities, AER, BAR, power-budget, DPA, secondary PCIe, and lane equalization registers through lane 7.

The address block comments in this chunk identify the hardware aperture regions:

- `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`, base `0xfffe12103000`
- `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`, base `0xfffe12104000`
- `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`, base `0xfffe12105000`
- `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp`, base `0xfffe12106000`
- `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`, base `0xfffe12107000`
- `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`, base `0xfffe12300000`
- `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`, base `0xfffe12301000`
- `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`, base `0xfffe12500000`

## Important APIs, Types, and Macros

There are no functions, structs, enums, or runtime APIs declared in this chunk. The API surface is a generated C preprocessor namespace:

- `regBIF_CFG_DEVx_EPFy_1_<REGISTER>` constants provide encoded SOC15/NBIO register addresses for PCIe configuration registers.
- `regBIF_CFG_DEVx_EPFy_1_<REGISTER>_BASE_IDX` constants identify the register base index used by AMDGPU's register-access helpers. All complete pairs in this chunk use base index `5`.
- Standard PCI config aliases include `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, `REVISION_ID`, `PROG_INTERFACE`, `SUB_CLASS`, `BASE_CLASS`, BARs, `ROM_BASE_ADDR`, `CAP_PTR`, and interrupt-line/pin fields.
- PCIe capability aliases include `PCIE_CAP_LIST`, `PCIE_CAP`, `DEVICE_CAP`, `DEVICE_CNTL`, `DEVICE_STATUS`, `LINK_CAP`, `LINK_CNTL`, `LINK_STATUS`, `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, and `LINK_STATUS2`.
- Interrupt capability aliases include MSI and MSI-X registers such as `MSI_CAP_LIST`, `MSI_MSG_CNTL`, `MSI_MSG_ADDR_LO`, `MSI_MSG_ADDR_HI`, `MSI_MSG_DATA`, `MSI_MASK`, `MSI_PENDING`, `MSIX_CAP_LIST`, `MSIX_MSG_CNTL`, `MSIX_TABLE`, and `MSIX_PBA`.
- Error and diagnostics aliases include AER registers such as `PCIE_UNCORR_ERR_STATUS`, `PCIE_UNCORR_ERR_MASK`, `PCIE_UNCORR_ERR_SEVERITY`, `PCIE_CORR_ERR_STATUS`, `PCIE_CORR_ERR_MASK`, `PCIE_ADV_ERR_CAP_CNTL`, `PCIE_HDR_LOG0..3`, and `PCIE_TLP_PREFIX_LOG0..3`.
- Resource and virtualization/security aliases include enhanced BAR capability registers, ACS, PASID, ARI, VC/resource controls, DPA, and power-budget capability registers.
- High-speed link aliases in the larger endpoint blocks include `PCIE_LINK_CNTL3`, `PCIE_LANE_*_EQUALIZATION_CNTL`, 16 GT/s capability/status entries, and lane margining controls/status fields.

Several symbolic names intentionally share the same encoded address because they name fields or logical views within the same PCI config dword. Examples repeated across blocks include `VENDOR_ID` and `DEVICE_ID`, `COMMAND` and `STATUS`, `DEVICE_CNTL` and `DEVICE_STATUS`, `LINK_CNTL` and `LINK_STATUS`, `PCIE_DPA_STATUS` and `PCIE_DPA_CNTL`, `PCIE_ACS_CAP` and `PCIE_ACS_CNTL`, `PCIE_PASID_CAP` and `PCIE_PASID_CNTL`, and `PCIE_ARI_CAP` and `PCIE_ARI_CNTL`.

## Control Flow

This chunk has no runtime control flow. It is preprocessor data used at compile time.

The effective flow is:

1. `nbio_v7_7.c` includes `nbio/nbio_7_7_0_offset.h` and the matching `nbio_7_7_0_sh_mask.h`.
2. AMDGPU NBIO code passes selected `reg...` constants to access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, and PCIe-port accessors.
3. The helper layer combines the register offset and base index with device instance information to reach the correct MMIO/register aperture.

Most symbols in this chunk are not directly referenced by the nearby `nbio_v7_7.c` logic in the current tree; they are still part of the generated register map and may be used by diagnostics, future ASIC support, or code paths outside the searched direct references.

## State and Persistence Behavior

The header itself stores no mutable state and performs no persistence. Its constants describe hardware-backed PCIe configuration and capability registers. Any state effects occur only when consumers read or write those registers through AMDGPU accessors.

The registers described here correspond to hardware state such as:

- PCI config identity, command/status, class code, BAR, ROM, and interrupt configuration.
- PCIe link capability, control, status, equalization, and higher-speed PHY state.
- MSI/MSI-X message address/data/masking and pending bits.
- AER correctable/uncorrectable error status, masks, severity policy, header logs, and TLP-prefix logs.
- ACS/PASID/ARI capability and control fields that affect PCIe isolation, address-space tagging, and function routing semantics.
- Power-management, power-budget, and dynamic power allocation fields.

Persistence is hardware-defined. Some registers are strap-derived, reset to ASIC defaults, latched by firmware/platform enumeration, or controlled by PCI/PCIe configuration mechanisms. Driver writes to control/mask/status registers may alter live device behavior but are not persisted by this header.

## Dependencies

Primary dependencies are architectural rather than C-level:

- SOC15/NBIO register addressing conventions used by AMDGPU.
- Matching shift/mask definitions in `nbio_7_7_0_sh_mask.h` for fields within these offsets.
- AMDGPU register access macros and helpers declared through the common AMDGPU headers.
- PCI/PCIe configuration-space layout, including PCI PM, PCIe capability, MSI/MSI-X, AER, ACS, PASID, ARI, DPA, LTR/secondary capability, VC, and link equalization structures.
- The generated ASIC register database that produced this offset file. Manual edits would risk drifting from silicon documentation and the paired mask header.

The chunk is under `sources/distributed-fs/ceph-client/`, but its technical integration is the vendored Linux AMDGPU driver source tree, not Ceph filesystem logic.

## Integration Points

The direct integration point observed in this tree is:

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c` includes this header and uses NBIO 7.7 register symbols for revision ID, memory size, doorbells, interrupt handling, HDP flushes, PCIe index/data ports, and NBIO initialization.

This specific chunk maps endpoint-function PCIe config spaces rather than the doorbell/HDP registers that `nbio_v7_7.c` most visibly touches. Its integration value is still important because the generated header must provide a complete ASIC register namespace for all NBIO subblocks. Downstream users can add reads/writes to these symbols without introducing raw offsets.

The base-index constants are part of the integration contract with AMDGPU's generated-register infrastructure. They must stay paired with the correct `reg...` constants so helpers resolve each register against the intended NBIO base segment.

## Risks and Edge Cases

- Raw offset correctness is critical. A wrong encoded address can read or write the wrong PCIe config register, potentially changing link state, interrupt routing, BAR decoding, AER policy, or isolation features.
- Shared-address aliases are expected for packed PCI config dwords. Reviewers should not deduplicate them casually; the different names preserve semantic intent for different bitfields in the paired mask header.
- The chunk boundary splits a macro pair: `regBIF_CFG_DEV2_EPF0_1_PCIE_LANE_7_EQUALIZATION_CNTL` appears inside this chunk, while its `*_BASE_IDX` is immediately after line 29000. Merge/reconciliation tooling should account for that boundary rather than treating the source as malformed.
- Many blocks are repetitive, but the larger `DEV1_EPF0` and `DEV2_EPF0` areas contain extended link and lane-control coverage not present in the shorter EPF blocks. Bulk generated changes should preserve these block-specific differences.
- Because these are generated ASIC definitions, manual formatting or renaming changes can break out-of-tree users or make future generated drops noisy.
- Capability registers such as ACS, PASID, ARI, AER, and DPA are security- and reliability-sensitive when written. Any future consumer code should use field masks from the matching `*_sh_mask.h` file and preserve reserved bits.

## Test Signals

Useful validation signals for this chunk are mostly static and integration-oriented:

- Compile AMDGPU code that includes `nbio_v7_7.c`; missing, renamed, or malformed macros fail at build time.
- Run a preprocessor or static check that every `reg...` define in the full header has the expected `reg..._BASE_IDX` pair. This chunk alone has one expected boundary exception at its final line.
- Compare the generated offsets against the authoritative NBIO 7.7.0 register database or a known-good generated header such as neighboring NBIO versions.
- Use `rg` for direct consumers before changing symbols; direct references in this tree include the header include from `amdgpu/nbio_v7_7.c`, while many individual endpoint config symbols may be latent API surface.
- On hardware, PCIe enumeration, link training, MSI/MSI-X interrupt delivery, AER logging, and GPU initialization are the practical smoke tests for regressions in these definitions.
- For runtime changes that start using these symbols, test suspend/resume, GPU reset, PCIe error handling, SR-IOV/virtualization paths if applicable, and link-speed/link-width negotiation.

### subset-b-003258: lines 29001-29660

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_offset.h lines 29001-29660

## Purpose

This chunk is the final slice of AMDGPU's generated NBIO 7.7 offset header. It defines preprocessor constants for NBIF/BIF PCIe configuration-space register addresses in device 2 endpoint-function blocks. The macros are register-map data only: they do not implement Ceph, distributed filesystem behavior, or executable AMDGPU control logic.

The range starts mid-block with the tail of `BIF_CFG_DEV2_EPF0_1`, covers a complete `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp` address block, then covers `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp` through ARI control and the file's closing include guard. The EPF1 block base comment is `0xfffe12501000`; the EPF2 block base comment is `0xfffe12502000`. The visible encoded register values are `0x3fff8090....` SOC15-style register identifiers, and every visible `_BASE_IDX` macro in the chunk has value `5`.

## Important APIs, Types, and Macros

There are no functions, structs, typedefs, enums, or storage objects in this chunk. The public API is the exact generated macro names and numeric constants:

- `regBIF_CFG_DEV2_EPF0_1_*` tail macros for the end of EPF0's PCIe extended capabilities.
- `regBIF_CFG_DEV2_EPF1_1_*` address macros for a complete endpoint-function PCI configuration image.
- `regBIF_CFG_DEV2_EPF2_1_*` address macros for another endpoint-function PCI configuration image, ending at ARI control.
- Matching `*_BASE_IDX` macros, all `5`, which select the NBIO register-base table entry expected by AMDGPU's SOC15 register helpers.

The assigned range contains 660 source lines and 649 `#define` entries: 324 register-address macros plus 325 `_BASE_IDX` macros. The count is uneven because line 29001 is only the base-index companion for an EPF0 lane-7 equalization register whose address appears in the previous chunk.

Important macro groups include:

- EPF0 tail: lane 8-15 equalization control, ACS, PASID, LTR, ARI, data-link feature capability/status, 16 GT/s PHY/link controls, parity mismatch status, 16 GT/s lane equalization controls, and lane margining controls/status for lanes 0-15.
- EPF1 conventional PCI header: vendor/device ID, command/status, revision and class code bytes, cache-line/latency/header/BIST, BAR1-BAR6, CardBus CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency.
- EPF1 capabilities: vendor capability, PCI power management, PCIe capability, device/link capability-control-status sets, device/link capability 2, MSI, MSI-X, vendor-specific enhanced capability, Advanced Error Reporting, BAR enhanced capability, power budget, DPA, ACS, PASID, and ARI.
- EPF2 mirrors the EPF1 layout from vendor/device ID through ARI control, with the same register spacing shifted from the `0x3fff809004xx` range to `0x3fff809008xx`.

Several names intentionally share the same encoded register value because multiple PCI config fields occupy different bit slices of the same 32-bit dword. Examples include `VENDOR_ID` and `DEVICE_ID`, `COMMAND` and `STATUS`, class-code bytes, MSI 32-bit versus 64-bit forms, `DPA_STATUS` and `DPA_CNTL`, ACS cap/control, PASID cap/control, and ARI cap/control.

## Control Flow and Runtime Behavior

This header has no runtime control flow. Its effective flow is compile-time substitution:

1. `amdgpu/nbio_v7_7.c` includes `nbio/nbio_7_7_0_offset.h` and the matching `nbio/nbio_7_7_0_sh_mask.h`.
2. Driver code passes `reg...` constants into SOC15/NBIO register helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, or related PCIe-port accessors.
3. When a register value needs bitfield interpretation or modification, the caller uses the same register prefix in `nbio_7_7_0_sh_mask.h` for field shifts and masks.
4. Hardware performs the actual PCIe configuration, capability-chain, status, interrupt, link, and error-reporting behavior.

The specific EPF1/EPF2 macros in this chunk are not directly referenced by C files in the current tree beyond inclusion of the whole generated header. They remain part of the exported ASIC register surface for generated-code compatibility, diagnostics, platform bring-up, and future call sites.

## State and Persistence

The chunk stores no software state, allocates no memory, performs no I/O, and persists nothing by itself. It names hardware state in NBIO-backed PCIe configuration registers.

State represented by these offsets includes:

- Endpoint identity and enumeration-visible configuration: vendor/device IDs, class code, command/status, BARs, ROM BAR, capability pointer, and interrupt routing fields.
- PCIe link and device policy: device control/status, link control/status, target speeds, completion timeout behavior, atomic operation capabilities, LTR/OBFF-related policy where represented in paired masks, and 16 GT/s link/equalization state.
- Interrupt configuration: MSI and MSI-X message control, address/data, mask, pending, table, and PBA registers.
- Error and diagnostic state: AER uncorrectable/correctable status, masks, severity, capability/control, header logs, TLP prefix logs, data-link feature status, parity mismatch status, lane equalization, and lane margining.
- Virtualization and isolation-adjacent capability state: ACS controls, PASID capability/control, ARI capability/control, and DPA/power-budget fields.

Persistence rules are hardware-defined, not encoded here. Some registers are writable configuration state that may survive until reset, FLR, link reset, suspend/resume, BACO, or driver reinitialization. Others are hardware-updated status, sticky error, log, or write-one-to-clear fields whose clear and side-effect behavior must be derived from PCIe and AMD NBIO documentation.

## Dependencies and Integration Points

The direct companion is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_7_0_sh_mask.h`, which supplies field-level `__SHIFT` and `_MASK` definitions for the same register names. These offset and mask headers must stay synchronized by ASIC generation; mixing NBIO 7.7 offsets with another generation's masks can compile cleanly while targeting the wrong address or field.

The main C integration point in this tree is `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c`, which includes this offset header and uses generated NBIO constants through AMDGPU SOC15 register access macros. That file demonstrates the intended access pattern for the generated constants, even though its active call sites mostly use other NBIO 7.7 registers outside this particular chunk.

Semantic dependencies include the PCI and PCI Express configuration-space layouts, MSI/MSI-X capability formats, AER, ACS, PASID, ARI, data-link feature capability, PCIe 4.0 16 GT/s PHY/equalization registers, lane margining, AMD's SOC15 register-indexing scheme, and AMD's generated NBIO 7.7 register database.

## Risks and Maintenance Notes

- The range starts at a chunk boundary with only `regBIF_CFG_DEV2_EPF0_1_PCIE_LANE_7_EQUALIZATION_CNTL_BASE_IDX`; the matching address macro is in the previous chunk.
- Repeated EPF layouts are easy to cross-wire. An EPF1 macro and EPF2 macro can differ only by prefix and address stride, so prefix mistakes may compile while reading or writing the wrong endpoint-function image.
- Overlapping dword aliases are intentional. Consumers must pair each offset with the correct field masks and access width rather than assuming each macro names a distinct 32-bit register.
- `_BASE_IDX` value `5` is part of the register-address contract. A wrong base index can route SOC15 accessors to the wrong NBIO aperture even if the encoded address literal looks correct.
- MSI/MSI-X, ACS, PASID, and ARI registers affect interrupts, DMA isolation, process address spaces, and function routing. Incorrect programming can create reliability or isolation failures.
- AER and TLP log offsets are diagnostic-sensitive. Misaddressing status/mask/severity/log registers can suppress errors, misclassify PCIe faults, or attribute logs to the wrong function.
- Link equalization, 16 GT/s status, and lane margining registers are lane-numbered and repetitive; off-by-one lane use can make bring-up or debug tooling tune the wrong lane.
- This is a generated header with no type safety, reset values, access permissions, ordering requirements, or firmware-ownership metadata.

## Test and Validation Signals

Useful validation signals for this chunk are:

- Compile AMDGPU code paths that include `nbio_7_7_0_offset.h`, especially `amdgpu/nbio_v7_7.c`, to catch syntax, guard, or duplicate-definition breakage.
- Cross-check every visible `regBIF_CFG_DEV2_EPF1_1_*` and `regBIF_CFG_DEV2_EPF2_1_*` address macro against a matching shift/mask register block in `nbio_7_7_0_sh_mask.h`.
- Run generated-header consistency checks that each address macro has a matching `_BASE_IDX` with value `5`, accounting for the first line's chunk-boundary exception.
- Compare EPF1 and EPF2 macro sets mechanically: the register names should mirror each other while the encoded addresses should advance by the expected `0x400` dword stride.
- Compare this NBIO 7.7 block against AMD's authoritative register database and against nearby NBIO generation headers only as a sanity signal, not as a substitute for ASIC-specific data.
- On supported hardware or simulation, read PCI config-space dumps for device 2 EPF1/EPF2 and verify identity, BAR, capability chain, PCIe, MSI/MSI-X, AER, ACS, PASID, and ARI offsets decode as expected.
- Exercise PCIe error observation where possible and confirm AER status/mask/severity/header-log/TLP-prefix-log offsets map to the intended endpoint function.
- Validate link training, 16 GT/s equalization, and lane margining tooling against the EPF0 tail offsets, checking that lane-numbered accesses target the expected physical/logical lanes.

## Chunk Boundary Notes

Lines 29001-29161 finish `BIF_CFG_DEV2_EPF0_1` from the lane-equalization tail through ACS, PASID, LTR, ARI, data-link feature, 16 GT/s PHY/link, parity mismatch, 16 GT/s lane equalization, and lane margining registers.

Lines 29164-29409 define the complete `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp` block from `VENDOR_ID` through `PCIE_ARI_CNTL`.

Lines 29412-29657 define `nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp` from `VENDOR_ID` through `PCIE_ARI_CNTL`. Lines 29659-29660 close the file's include guard.
