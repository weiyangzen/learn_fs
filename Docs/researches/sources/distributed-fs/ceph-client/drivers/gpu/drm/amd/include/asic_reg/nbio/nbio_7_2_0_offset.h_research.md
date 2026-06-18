# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003146`: lines 1-2409, `Docs/researches/chunks/subset-b-003146_research.md`
- `subset-b-003147`: lines 2410-4857, `Docs/researches/chunks/subset-b-003147_research.md`
- `subset-b-003148`: lines 4858-7354, `Docs/researches/chunks/subset-b-003148_research.md`
- `subset-b-003149`: lines 7355-9783, `Docs/researches/chunks/subset-b-003149_research.md`
- `subset-b-003150`: lines 9784-12207, `Docs/researches/chunks/subset-b-003150_research.md`
- `subset-b-003151`: lines 12208-14624, `Docs/researches/chunks/subset-b-003151_research.md`
- `subset-b-003152`: lines 14625-17031, `Docs/researches/chunks/subset-b-003152_research.md`
- `subset-b-003153`: lines 17032-19461, `Docs/researches/chunks/subset-b-003153_research.md`
- `subset-b-003154`: lines 19462-21877, `Docs/researches/chunks/subset-b-003154_research.md`
- `subset-b-003155`: lines 21878-24223, `Docs/researches/chunks/subset-b-003155_research.md`
- `subset-b-003156`: lines 24224-26565, `Docs/researches/chunks/subset-b-003156_research.md`
- `subset-b-003157`: lines 26566-28914, `Docs/researches/chunks/subset-b-003157_research.md`
- `subset-b-003158`: lines 28915-31260, `Docs/researches/chunks/subset-b-003158_research.md`
- `subset-b-003159`: lines 31261-31871, `Docs/researches/chunks/subset-b-003159_research.md`

## Chunk Research

### subset-b-003146: lines 1-2409

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

### subset-b-003147: lines 2410-4857

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 2410-4857

## Scope And Purpose

This chunk is part of AMDGPU's generated NBIO 7.2.0 register offset map. It contains only preprocessor constants: register/config-space offsets plus matching `_BASE_IDX` constants that identify the SOC15 base-index table entry used by `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and the PCIe-port access helpers. There are no C functions or runtime control flow in this chunk; its purpose is to provide the numeric ABI between NBIO v7.2 driver code and the GPU's PCIe/NBIO/GDC hardware register layout.

The chunk begins in the middle of the `cfgBIFPLR1_*` PCIe config-space root-port capability map, fully covers `cfgBIFPLR2_*` through `cfgBIFPLR6_*`, then defines NBIF/RCC/BIF/GDC/SYSHUB/RAS/reset address blocks and the first root-complex config-space offsets. The final per-file report should merge this with adjacent chunks because several logical register families begin before line 2410 or continue after line 4857.

## Address Blocks Covered

- Continuation of `cfgBIFPLR1_*`: MSI, SSID, MSI map, vendor-specific, VC, AER, secondary PCIe, ACS, multicast, L1 PM substate, DPC, ESM, DLF, 16 GT/s PHY, lane margining, CCIX, and translation control config offsets.
- `nbio_pcie0_bifplr2_cfgdecp` through `nbio_pcie0_bifplr6_cfgdecp`, base `0x0`: repeated PCIe root-port config-space layouts. Each port family includes vendor/device/class/header/BAR/bridge-window fields, PM/PCIe/MSI capabilities, AER, ACS, DPC, lane equalization, 16 GT/s capability, margining, CCIX, and translation-control registers.
- `nbio_nbif0_bif_bx_pf_SYSPFVFDEC:1`, base `0x0`: PF indexed MMIO and RSMU index/data apertures, including `regBIF_BX_PF0_MM_INDEX`, `regBIF_BX_PF0_MM_DATA`, `regBIF_BX_PF0_MM_INDEX_HI`, `regBIF_BX_PF0_RSMU_INDEX`, and `regBIF_BX_PF0_RSMU_DATA`.
- `nbio_nbif0_bif_bx_SYSDEC:1`, base `0x0`: PCIe index/data pairs, SBIOS/BIOS scratch registers, BIF interrupt controls, graphics MMIO CAM address/remap slots, and programmable completion behavior.
- `nbio_nbif0_rcc_strap_BIFDEC1`, base `0x0`: RCC BIF, port, endpoint-function, and EPF1 strap offsets. These represent latched hardware strap/configuration state such as revision and feature exposure.
- `nbio_nbif0_rcc_ep_dev0_BIFDEC1:1`, `nbio_nbif0_rcc_dwn_dev0_BIFDEC1:1`, and `nbio_nbif0_rcc_dwnp_dev0_BIFDEC1:1`, base `0x0`: endpoint/downstream PCIe control, scratch, interrupt, DPA, PME, requester ID, error, RX, link-speed, LTR, and strap registers.
- `nbio_nbif0_rcc_dev0_epf0_BIFPFVFDEC1`, base `0x0`: PF/VF-facing RCC error log, doorbell aperture enable, config memory size, config reserved fields, and IOV function identifier offsets. Many entries have `_1` and `_2` aliases with the same offset/base index.
- `nbio_nbif0_rcc_dev0_BIFDEC1:1`, base `0x0`: RCC device-level error interrupt, BACO/reset, VDM, margining, GPU IOV, host VM, peer register ranges, bus/config aperture, XDMA, bus-number, peer framebuffer offsets, link control, requester-ID restore, LTR, and arbitration offsets.
- `nbio_nbif0_bif_bx_BIFDEC1:1`, base `0x0`: BIF strap/pinstrap, indirect-access control, bus control, scratch, reset, interrupt, doorbell, framebuffer enable, transaction-pending, address LUT, HDP remap flush, and BIF ring-buffer offsets.
- `nbio_nbif0_bif_bx_pf_BIFPFVFDEC1:1`, base `0x0`: PF-specific BME status, atomic error logging, self-ring doorbell GPA aperture, HDP coherency flush/invalidate controls, GPU HDP flush request/done registers, transaction-pending status, and address-LUT bypass.
- `nbio_nbif0_rcc_dev0_epf0_BIFDEC2`, base `0x0`: GFX MSI-X vector table and pending-bit-array offsets for vectors 0-3, again with duplicated `_1` and `_2` aliases.
- `nbio_nbif0_gdc_GDCDEC`, base `0x1400000`: GDC/NGDC SDP and SHUB interface control, NBIF graphics doorbell status, SDMA/IH/VCN/RLC doorbell ranges, ATDMA/S2A controls, doorbell fence control, and SHUBCLK DPM counters/weights.
- `nbio_nbif0_syshub_mmreg_syshubdirect`, base `0x1400000`: OBFF emulation registers for SOCCLK/SHUBCLK/NICCLK and host clock switch/client controls.
- `nbio_nbif0_gdc_ras_gdc_ras_regblk`, base `0x1400000`: RAS error-response controls, central status, leaf controls, and leaf status for GDC SOC, SHUB, and NIC subdomains.
- `nbio_nbif0_gdc_rst_GDCRST_DEC`, base `0x1400000`: SHUB PF FLR, VPU driver reset, link reset, hard/soft reset, SDP port reset, and reset trail/misc offsets.
- Start of `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`, base `0x10100000`: root-complex PCI config header offsets for vendor/device ID, command/status, revision/class, cache/latency/header/BIST, BARs, bus numbers, and IO base/limit.

## Important Macros And Hardware APIs

The exported API surface is the macro namespace itself. Consumers include `nbio_v7_2.c`, which includes this file and the matching `nbio_7_2_0_sh_mask.h`. Representative consumer paths are:

- HDP remap and flush: `regBIF_BX0_REMAP_HDP_MEM_FLUSH_CNTL`, `regBIF_BX0_REMAP_HDP_REG_FLUSH_CNTL`, `regBIF_BX_PF0_GPU_HDP_FLUSH_REQ`, and `regBIF_BX_PF0_GPU_HDP_FLUSH_DONE`.
- Framebuffer and memory-controller access: `regBIF_BX0_BIF_FB_EN` and `regRCC_DEV0_EPF0_0_RCC_CONFIG_MEMSIZE`.
- Doorbells: `regRCC_DEV0_EPF0_0_RCC_DOORBELL_APER_EN`, `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_BASE_LOW/HIGH`, `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_CNTL`, `regGDC0_BIF_SDMA0_DOORBELL_RANGE`, `regGDC0_BIF_IH_DOORBELL_RANGE`, `regGDC0_BIF_VCN0_DOORBELL_RANGE`, and `regGDC0_BIF_RLC_DOORBELL_RANGE`.
- Interrupt handling: `regBIF_BX0_INTERRUPT_CNTL`, `regBIF_BX0_INTERRUPT_CNTL2`, `regBIF_BX0_BIF_INTR_CNTL`, and doorbell interrupt controls.
- PCIe indirect/config access: `regBIF_BX0_PCIE_INDEX2`, `regBIF_BX0_PCIE_DATA2`, `regBIF_BX_PF0_RSMU_INDEX`, `regBIF_BX_PF0_RSMU_DATA`, plus the `cfgBIFPLR*_*` PCI config offsets.
- Reset and fault handling: `regSHUB_*_RST*`, `regGDCSOC_*`, `regGDCSHUB_*`, and `regGDCNIC_*`.

Each register macro is usually paired with a `_BASE_IDX` macro. Base indices visible in this chunk include `0` for direct/indexed MMIO windows, `1` for SBIOS/BIOS scratch and related SYSDEC registers, `2` for RCC/BIF BIFDEC1 spaces, `3` for GDC/SYSHUB/RAS/MSI-X/GDCRST spaces, and `5` for root-complex config space. The exact interpretation is supplied by the SOC15 register base table, not by this header.

## Control Flow

This chunk does not execute. Driver control flow enters through other AMDGPU modules, primarily NBIO setup paths, which pass these constants to register access macros. The practical flow is:

1. Driver code selects NBIO instance and register family.
2. `SOC15_REG_OFFSET(NBIO, instance, reg...)` combines a macro value, its base index, and the device's discovered register-base table.
3. Access helpers such as `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, and `WREG32_PCIE_PORT` issue MMIO or PCIe-port reads/writes.
4. Matching masks from `nbio_7_2_0_sh_mask.h` are used to edit fields with `REG_SET_FIELD()` or to test completion/status bits.

Because the file is generated offset data, the runtime branching, locking, polling, and error handling all live in consuming C files. For example, `nbio_v7_2.c` uses these offsets to enable or disable framebuffer access, remap HDP flush registers, program doorbell ranges, configure IH dummy reads, and expose PCIe index/data offsets to common AMDGPU code.

## State And Persistence Behavior

The macros name persistent hardware state, but the header itself stores no software state. The underlying registers cover several state categories:

- Configuration state exposed through PCIe config-space capability lists and root-port headers.
- Latched strap state under `regRCC_STRAP0_*`, read by the driver for revision/feature information.
- Runtime-programmed aperture state, including framebuffer enable, doorbell aperture enable, self-ring doorbell GPA base, and config aperture sizing.
- Interrupt and ring state, including dummy-page address programming, BIF interrupt routing, transaction-pending indicators, and BIF ring-buffer pointer/base registers.
- Reset and RAS state for SHUB/GDC subdomains, where status bits may survive until cleared according to hardware semantics.
- BIOS/SBIOS scratch registers, which are integration points with firmware and may carry boot-time or handoff values.

Persistence is hardware-defined. Writes to many of these registers can persist across a driver mode-setting phase until device reset, FLR, BACO transition, or full GPU reset. Scratch, strap, config-space, and RAS status semantics should be treated as externally shared with firmware, the PCI core, and hardware recovery paths.

## Dependencies And Integration Points

This header is tightly coupled to:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, the direct NBIO v7.2 consumer for many `regBIF_BX0_*`, `regBIF_BX_PF0_*`, `regGDC0_*`, and `regRCC_*` offsets in this chunk.
- `nbio_7_2_0_sh_mask.h`, which provides field masks/shifts for the same register names. Offsets and masks must match the same hardware generation.
- SOC15 register access infrastructure, especially `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, and PCIe-port variants.
- PCI/PCIe architecture conventions for config-space offsets, AER/DPC/ACS/MSI/MSI-X, L1 PM substates, CCIX, 16 GT/s equalization, and root-port capabilities.
- AMDGPU interrupt, doorbell, KFD, reset, RAS, BACO, and memory-controller flows. The offsets are not Ceph-specific despite this repository path being under `sources/distributed-fs/ceph-client`; they belong to the vendored Linux AMDGPU driver tree.

The duplicate `_1` and `_2` aliases for some EPF0/MSI-X/config registers are notable integration details. They indicate multiple generated views or function aliases that intentionally resolve to the same offset/base index; consumers must not assume every macro name maps to a unique address.

## Risks And Edge Cases

- A wrong offset or `_BASE_IDX` silently targets the wrong hardware register. Effects range from no-op feature setup to corrupted PCIe aperture, lost interrupts, broken doorbells, invalid HDP cache flushing, or reset/RAS misbehavior.
- The `cfgBIFPLR*_*` families are highly repetitive. Copy/paste or generation errors are hard to catch by visual review, especially where halfword config-space offsets share the same dword address.
- Some symbols in this chunk are only aliases to the same address, such as MSI data/address overlaps and `_1`/`_2` replicated generated names. Tooling that deduplicates names or assumes one semantic field per offset can lose information.
- The chunk starts and ends mid-family. `cfgBIFPLR1_*` is incomplete at the start, and `regBIF_CFG_DEV0_RC0_*` continues after the chunk. Whole-file analysis must reconcile neighboring chunks before making completeness claims.
- Register access helper choice matters. Some GDC doorbell range registers are used through PCIe-port access helpers in `nbio_v7_2.c`, while many BIF/RCC registers are accessed through SOC15 helpers. Mixing access paths can break on platforms where indexed and direct windows differ.
- Generated headers are usually hardware-contract files. Local hand edits are risky unless backed by a newer register database, silicon documentation, or a proven upstream patch.

## Test And Validation Signals

- Build coverage should compile AMDGPU files that include `nbio_7_2_0_offset.h`, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, with `nbio_7_2_0_sh_mask.h` present and matching.
- Runtime smoke tests on NBIO 7.2-family hardware should verify GPU probe, PCIe config access, VRAM/framebuffer enable, interrupt delivery, KFD/HDP flush remapping, SDMA/IH/VCN doorbell operation, and suspend/resume or reset flows.
- Hardware diagnostics should inspect that programmed doorbell ranges match expected doorbell indices and sizes, and that HDP flush request/done bits transition for CP/SDMA clients.
- RAS validation should inject or surface NBIO/GDC/SYSHUB/NIC errors where supported and confirm central/leaf status registers are read from the expected addresses.
- Regression checks should compare this generated offset set against upstream AMDGPU NBIO 7.2.0 headers or the authoritative ASIC register source, including duplicate alias handling and base-index values.

### subset-b-003148: lines 4858-7354

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 4858-7354

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 register-offset header segment. It contains 2,397 `#define` lines: 1,199 register-offset macros and 1,198 companion `_BASE_IDX` macros. There are no C functions, structs, enums, variables, loops, branches, allocations, locks, or executable statements in this range.

The range starts in the middle of `nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`, beginning at `regBIF_CFG_DEV0_RC0_SECONDARY_STATUS`, completes the remainder of the dev0 root-complex PCIe configuration block, covers complete dev1 and dev2 root-complex config blocks, then moves through NBIF system/PF windows, RCC strap tables, endpoint and downstream-port control blocks, RCC port-decoder copies for dev0/dev1/dev2, and the beginning of `nbio_nbif0_bif_misc_bif_misc_regblk` through `regBIFC_HSTARB_CNTL`. Adjacent chunks are required to see the earlier dev0 RC0 identity/command registers and the rest of the BIF misc register block.

Although the repository path is under a `ceph-client` source mirror, this file is AMD GPU hardware register metadata. It has no direct Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_offset.h` provides symbolic offsets for NBIO 7.2.0 registers. Each register macro names a hardware register and maps it to the offset value expected by AMDGPU's generated register access helpers. Each `_BASE_IDX` macro identifies the SOC15 base-index selector used with that offset; every macro in this chunk uses base index `5`.

The chunk gives driver code stable symbolic names for PCIe root-complex configuration, PCIe capability structures, advanced error reporting, virtual-channel/resource controls, lane margining, root-complex controller straps, endpoint/downstream port controls, NBIF mailbox and indirect MMIO windows, DMA attribute overrides, interrupt-line controls, BME/error logging, and host-arbitration/misc controls. The constants are meant to be paired with companion shift/mask/default headers and AMDGPU register helper macros rather than used as standalone behavior.

## Important Macro Families

The first family is the tail of `regBIF_CFG_DEV0_RC0_*` and complete `regBIF_CFG_DEV1_RC0_*` / `regBIF_CFG_DEV2_RC0_*` root-complex configuration blocks. These cover PCI bridge base/limit windows, capability pointers, ROM base, interrupt-line/pin/bridge control, power-management capability, PCIe capability, device/link/slot/root capabilities and controls, MSI, subsystem ID, MSI map, vendor-specific and virtual-channel enhanced capabilities, device serial number, AER status/mask/severity/header-log/root-error registers, TLP prefix logs, secondary PCIe capability, link-control 3, lane-error status, lane equalization controls for lanes 0-15, ACS capability/control, and lane margining controls/status for lanes 0-15.

The `nbio_nbif0_bif_bx_pf_SYSPFVFDEC` and `nbio_nbif0_bif_bx_SYSDEC` groups define PF1 indirect MMIO index/data access and system-level BIF/NBIF registers. These include PCIe index/data windows, scratch registers, mailbox registers, host-power-management control, revision ID, misc/project ID registers, MSI-to-SMI steering, BME reset/pending logging, debug mux, FLR controls, reset logic, clock request, hotplug/PME/DEC error interrupt status and masks, SERR/GFX interrupt status, SWUS/SWUS2 trap controls, and GFX MMIO register CAM programmable request/completion controls.

The `nbio_nbif0_rcc_strap_BIFDEC1:1` and `nbio_nbif0_rcc_strap_rcc_strap_internal` groups are strap-table definitions for the RCC and PCIe endpoints. They include common BIF straps, device/port straps, upstream/downstream port straps, Gen3/Gen4 equalization control, link configuration straps, PCIeP hardware-debug controls, ACPI/PME straps, PCIe clock/power controls, BAR/window sizing, DPA power-allocation straps, and EP function-specific strap sets for dev0/dev1/dev2. These macros describe latched hardware configuration policy exposed through NBIO register space.

The `RCC_EP_*`, `RCC_DWN_*`, and `RCC_DWNP_*` blocks repeat for dev0 in `BIFDEC1`, then for dev0/dev1/dev2 in `RCCPORTDEC`. Endpoint blocks define scratch/control, interrupt control/status, RX/TX/LTR/cfg/bus controls, strap misc registers, DPA capability/control/substate power allocation, PME control, TX requester ID, error control, RX control, and link-speed control. Downstream blocks define reserved/scratch/control/config/RX/bus/cfg/strap registers. Downstream-port blocks define error control, RX control, link-speed control, link-control 2, PCIeP strap misc, and LTR message information received from endpoints.

The `RCC_DEV*` controller blocks expose VDM support, bus control, feature/misc control, link control, common link control, requester-ID restore, LTR switch control, multi-host arbitration, and margining parameter controls. The earlier `regRCC_DEV0_1_*` group also includes RCC error interrupt control/status, signal outputs, feature toggles, power management, filter controls, address translation controls, tag controls, FLR controls, and BME error logging.

The `BIF_BX1_*` and `BIF_BX_PF1_*` groups cover BIF bridge/controller support around BME, interrupts, FLR, straps, debug, SDP, virtual-machine/hypervisor mailbox, and trap or shadow-access plumbing. The final partial `bif_misc` group begins global NBIF/BIF miscellaneous controls: BIOS strap control, scratch, interrupt-line polarity/enable, outstanding virtual-channel allocation, BIFC misc controls, BME error logs, link-controller timer control, RCC/BIH BME error logs, per-device/per-function DMA attribute override registers, DMA attribute control per device, dummy BME controls, and host arbitration control.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor namespace:

- `reg<name>` macros provide register offsets.
- `reg<name>_BASE_IDX` macros provide the SOC15 base-index selector.

The header does not define bit positions, masks, reset values, access widths, read/write permissions, write-one-to-clear behavior, reset-domain ownership, or sequencing requirements. Consumers must combine these offsets with NBIO 7.2.0 shift/mask/default headers and AMDGPU access helpers such as SOC15 register read/write macros, PCI config-space access paths, SMN paths, or indirect MMIO helpers selected by the owning code. In this tree, `nbio_7_2_0_offset.h` is included by `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` and by DCN 3.01/3.1 display resource code.

## Control Flow

This header has no local runtime control flow. The implied external flow is:

1. ASIC-specific code selects an NBIO 7.2.0 register macro and base index.
2. The AMDGPU register helper computes the MMIO, config, or indirect access target for the active device.
3. Driver code reads status, decodes fields with companion shift/mask definitions, or writes a value that was composed according to the hardware spec.
4. Hardware side effects occur in PCIe/NBIO/RCC blocks, not in this header.

The register names point at hardware flows that are asynchronous to software: PCIe enumeration and bridge aperture setup, link training and equalization, lane-margining diagnostics, MSI and PME routing, AER status capture and clearing, virtual-channel/resource allocation, FLR/reset handling, strap-latched configuration, endpoint/downstream LTR messaging, BME and atomic/DMA attribute policy, mailbox communication, and interrupt/status propagation.

## State And Persistence Behavior

The header owns no memory and persists nothing. It describes addresses for hardware-visible state. Persistence of the represented state depends on PCIe reset, GPU reset domains, power-gating state, strap latch timing, BIOS/firmware initialization, PSP/SMU ownership, suspend/resume restore, and explicit driver writes.

Represented state includes PCI bridge identity/control/status, base/limit windows, capability and error-reporting status, link/slot/root state, lane equalization and margining controls/status, root-complex strap policy, endpoint/downstream port configuration, LTR and PME settings, DPA substate power allocation, requester IDs, BME and DMA attribute overrides, interrupt-line polarity/enables, scratch/mailbox contents, FLR/reset controls, and host arbitration settings.

Several register names indicate latched or side-effect-prone hardware state (`STATUS`, `INT_STATUS`, `ERR_LOG`, `SCRATCH`, `FLR`, `RESET`, `DPA`, `PME`, `LTR`, and strap registers). The offset header does not specify which bits are read-only, write-one-to-clear, sticky across resets, firmware-owned, or preserved across power transitions; callers must use the hardware programming guide and companion generated metadata.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must stay synchronized with sibling headers for shifts, masks, defaults, and other address forms. Cross-generation headers contain similarly named macros, but base indices and register coverage can differ; NBIO 7.2.0 consumers should include the generation-specific header selected by the ASIC implementation.

Primary integration points are AMDGPU NBIO initialization and service code, PCIe root-complex handling, display code paths that need NBIO offsets for DCN resource setup, RAS/AER diagnostics, hotplug/PME and interrupt routing, FLR/GPU reset recovery, virtualization/PF mailbox paths, BME and DMA attribute policy, and power-management/link-management code. The endpoint/downstream/RCC blocks tie software-visible PCIe controls to root-complex controller hardware rather than to ordinary Linux PCI core data structures alone.

## Risks And Edge Cases

- Generated offset drift can compile successfully while sending reads or writes to the wrong register, causing PCIe enumeration failures, broken link training, missed error status, false interrupts, or reset/hotplug regressions.
- This chunk begins mid-address-block. The dev0 RC0 identity, command/status, BAR, and early bridge registers are in the prior chunk; final per-file research must merge both ranges before treating dev0 RC0 coverage as complete.
- This chunk also ends mid-`bif_misc` block at `regBIFC_HSTARB_CNTL`; later BIF misc controls are outside this research item.
- Many offsets deliberately alias the same dword for adjacent PCI config fields, such as control/status halves or MSI/DPA subfields. Callers must use the correct companion bit masks and preserve unrelated fields during read-modify-write operations.
- The dev0/dev1/dev2 and endpoint/downstream blocks are highly patterned. A single generated mismatch in one device or lane can produce topology-specific failures that do not reproduce on simpler configurations.
- Strap and reset/FLR registers can alter persistent hardware policy or reset active devices. Writes must be sequenced with firmware ownership, quiescing, and restore expectations.
- AER, BME, interrupt, PME, LTR, and DMA attribute registers can affect error visibility and transaction ordering. Incorrect programming can hide fatal errors, generate interrupt storms, or change DMA behavior.
- Lane equalization and margining controls are link-training sensitive. Diagnostic writes should be bounded, restore reserved bits, and account for active traffic and retrain requirements.

## Test Signals

- Build AMDGPU with NBIO 7.2.0 support enabled; compile coverage catches removed or renamed generated symbols used by `nbio_v7_2.c`, DCN resource code, and other consumers.
- Run generated-header consistency checks: each register macro in the chunk should have exactly one `_BASE_IDX` companion, base-index values should match the NBIO 7.2.0 address map, and patterned dev/lane/function blocks should be internally aligned.
- Cross-check offsets against NBIO 7.2.0 shift/mask/default headers and the hardware register database, especially aliased PCI config dwords, DPA substate registers, AER log/status registers, and repeated RCC endpoint/downstream blocks.
- On supported hardware, validate PCIe enumeration, bridge aperture setup, link speed/width reporting, link retrain/equalization, lane-margining diagnostics, MSI/PME behavior, AER logging, and hotplug or reset recovery.
- Exercise suspend/resume and GPU reset/FLR paths while tracing RCC strap-derived settings, endpoint/downstream controls, BME logs, and interrupt status to confirm state is restored or intentionally reinitialized.
- For virtualization or multi-function configurations, validate PF mailbox/shadow/trap paths, BME status, DMA attribute overrides per device/function, requester ID programming, and LTR message handling.

### subset-b-003149: lines 7355-9783

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 7355-9783

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 register-offset header segment. It contains 2,401 `#define` macros over 2,429 source lines, all in the `reg*` namespace. The macros alternate between register offset constants and their matching `<REGISTER>_BASE_IDX` selector constants, with the base index fixed to `5` throughout this range.

The range starts inside the `nbio_nbif0_bif_misc_bif_misc_regblk` block at `regBIFC_HSTARB_CNTL_BASE_IDX`, then covers complete NBIF reset, RAS, SION, and PCIe endpoint-function configuration blocks for device 0 functions EPF0 through the beginning of EPF3. It ends at `regBIF_CFG_DEV0_EPF3_0_MSI_PENDING_64_BASE_IDX`, so the EPF3 PCIe configuration block continues in the following chunk.

Although the repository path is under a `ceph-client` source mirror, this file is AMDGPU hardware register metadata and has no direct Ceph or distributed-filesystem logic.

## Purpose

`nbio_7_2_0_offset.h` provides symbolic register offsets for the NBIO 7.2.0 ASIC register map. Driver code uses these constants with AMDGPU register-access helpers and companion shift/mask/default headers so call sites can name hardware registers instead of embedding raw offsets.

This chunk maps NBIO/BIF control registers, reset controls, RAS reporting registers, SION buffer/credit controls, and PCIe configuration-space windows for several GPU endpoint functions. The constants are address metadata only: they do not define bitfields, reset values, access permissions, side effects, or register sequencing.

## Important Macro Families

The opening partial `nbio_nbif0_bif_misc_bif_misc_regblk` tail covers BIF/NBIF miscellaneous control and status offsets around `0xe829`-`0xe8d2`. Important groups include BIFC GSI and PCIe function controls, PASID check/status controls, SDP controls, ATHUB activation, MMIO/DMA performance counters, NBIF register-interface error-set control, NBIF power-gating master/slave/misc controls, host miscellaneous controls, SMN master endpoint controls, strap write control, INTx D-state and pending controls, GMI weighted round-robin controls, power-break request, atomic/PASID/DMA error logs, OBFF emulation, endpoint urgent interrupt capabilities, pending block masks, virtual-wire controls, LCLK clock/deep-sleep controls, SHUB timeout detector registers, SDP/SST pool-credit allocation, BDF controls, and early wakeup control.

The complete `nbio_nbif0_bif_rst_bif_rst_regblk` block starts at line 7522 and contributes 186 macros. It maps hard and self soft reset controls, VPU/GFX driver reset controls, BIF reset miscellaneous controls, per-device and per-function FLR reset controls for device 0 functions 0-7, device 1 functions 0-7, and device 2 functions 0-7, FLR power-state-change request/status/enable registers, FLR request disable registers, reset request disable registers, reset sticky/status registers, host reset straps, software scratch reset cleanup controls, reset monitoring controls, per-function reset pulse counters, bus and device reset controls, hot reset controls, and per-port D-state value registers.

The complete `nbio_nbif0_bif_ras_bif_ras_regblk` block contributes 24 macros. It maps BIFL RAS central control, error status, BIFL-to-host and BIFL-to-IOHUB virtual-wire control/status registers, and virtual-wire source registers. These offsets integrate NBIO error reporting with broader RAS and sideband notification paths.

The complete `nbio_nbif0_nbif_sion_SIONDEC` block contributes 124 macros. It maps SION client read-response, write-response, request, and data buffer target registers for clients CL0 through CL8, per-client buffer status registers, read/write buffer-credit registers, accumulated credit counters, and global SION control registers. These offsets describe NBIF/SION buffering and flow-control state rather than software queues.

The `nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` and `nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` blocks each contribute 702 macros. They provide PCI-compatible configuration registers for device 0 endpoint functions 0 and 1, including vendor/device identity, command/status, class/revision, BARs, ROM BAR, interrupt metadata, vendor capability, power-management capability, PCIe capability, device/link capability and control/status pairs, MSI registers, subsystem ID, MSI mapping, PCIe vendor-specific, VC, serial number, AER, secondary PCIe, ACS, data-link feature, 16 GT/s PHY, lane margining, physical-layer, latency tolerance reporting, link declaration, multicast, atomic-op routing, PASID, LTR, and TPH requestor/ST table registers. They also include large AMD GPU-IOV vendor-specific scheduling/header register windows for SDMA, VCE, UVD, and related engine scheduling controls.

The `nbio_nbif0_bif_cfg_dev0_epf2_bifcfgdecp` block contributes 378 macros. It mirrors the standard PCIe endpoint configuration structure for device 0 function 2 through TPH requestor and TPH steering-table entries, but this range does not include the larger GPU-IOV scheduling windows present for EPF0 and EPF1.

The final `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp` block starts at line 9662 and contributes 120 macros in this chunk. It covers the early PCIe configuration-space portion of device 0 function 3: identity, command/status, class/header, BARs, ROM BAR, interrupts, vendor and power-management capabilities, PCIe device/link capability and control/status pairs, second-generation device/link capability and control/status pairs, and MSI address/data/mask/pending registers. The rest of EPF3 follows after line 9783.

## APIs, Types, And Functions

There are no callable APIs, C types, functions, variables, allocations, locks, or executable statements in this chunk. The public interface is the preprocessor macro namespace:

- `reg<NAME>` macros encode NBIO register offsets, usually in dword-indexed SOC15-style form.
- `reg<NAME>_BASE_IDX` macros encode the base-instance selector used by AMDGPU register helpers; all values in this range are `5`.

Consumers are expected to combine these macros with sibling generated headers such as `nbio_7_2_0_sh_mask.h` for field layout and any default-value metadata for reset values. The header itself cannot tell a caller whether a register is read-only, write-one-to-clear, sticky across reset, firmware-owned, or safe to touch during power transitions.

## Control Flow

This header has no local runtime control flow. Runtime flow is external and typically follows this pattern:

1. AMDGPU code selects the NBIO 7.2.0 register symbol matching the active ASIC and hardware block.
2. Register helper macros use the `reg*` offset plus the `_BASE_IDX` selector to compute the target MMIO or indexed-register address.
3. Driver code reads, writes, or read-modify-writes the hardware register using companion shift/mask macros to isolate fields.
4. Hardware then performs the configured operation, such as changing PCIe configuration state, reporting an error, gating a link/control path, initiating or observing reset state, or exposing SION credit/status information.

The implied hardware flows include PCIe enumeration and capability walking, MSI programming, function-level reset handling, hot reset and D-state transitions, PASID and atomic-operation error logging, NBIF power/clock gating, RAS virtual-wire signaling, SION buffer-credit accounting, PCIe advanced error reporting, lane margining, LTR/TPH configuration, and GPU-IOV engine scheduling configuration.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes offsets for hardware-visible state inside NBIO/BIF registers and PCIe configuration windows.

State represented by this chunk includes reset request/status/sticky bits, FLR controls, D-state values, strap and virtual-wire settings, PASID/atomic/DMA error logs, performance counters, power-gating and clock-gating controls, timeout-detector state, SION buffer occupancy and credits, PCI configuration identity/control/status registers, BAR and ROM aperture registers, MSI address/data/mask/pending state, PCIe capability and AER status, lane margining controls, LTR and TPH policy, and GPU-IOV scheduler/vendor-specific state for selected endpoint functions.

Persistence depends on the hardware reset domain, PCIe reset type, FLR, hot reset, power gating, firmware/BIOS initialization, PSP/SMU ownership, suspend/resume restore, and explicit driver writes. Several names in this range indicate sticky or latched state (`*_STATUS`, `*_STS`, `*_ERR_LOG`, `*_ERR_CLR`, `*_RST_STICKY`, MSI pending/mask registers), but the offset header does not define clear behavior or read side effects.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database and must stay synchronized with sibling offset, shift/mask, and default headers for the same IP version. It is included through AMDGPU ASIC register include paths under `drivers/gpu/drm/amd/include/asic_reg/nbio`.

Primary integration points are AMDGPU NBIO initialization, PCIe configuration and capability handling, GPU reset and FLR paths, runtime power management, interrupt/MSI setup, RAS/error handling, virtualization/GPU-IOV configuration, SION/NBIF flow-control diagnostics, SMN/ATHUB interaction, and suspend/resume or hotplug recovery paths.

The PCIe endpoint-function blocks align closely with standard PCI configuration-space concepts. They are integration points between Linux PCI core expectations, AMDGPU ASIC-specific register access, firmware-populated strap/default state, and virtualized function exposure. The reset and RAS blocks integrate with recovery paths that must coordinate host-visible PCIe state, internal NBIO state, SMU/PSP handling, and user-visible GPU reset behavior.

## Risks And Edge Cases

- Generated-offset drift can compile cleanly but direct reads or writes to the wrong NBIO register, causing PCIe enumeration failures, broken MSI setup, missed errors, unstable reset recovery, or incorrect virtualization state.
- This chunk starts and ends mid-block. The preceding chunk is needed for the beginning of `nbio_nbif0_bif_misc_bif_misc_regblk`, and the following chunk is needed to complete `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`.
- All macros use base index `5`. A consumer that assumes a different SOC15 base instance for NBIO 7.2.0 will access the wrong register aperture even if the offset constant is correct.
- Many PCIe configuration fields share the same dword offset, for example status/control pairs or MSI address/data aliases. Callers must use proper field masks and access widths to avoid clobbering adjacent fields.
- Reset and FLR registers are sequencing-sensitive. Writing disable, request, pulse-count, hot-reset, or sticky-status registers without the required waits can leave functions partially reset or make recovery failures intermittent.
- Error-log and status-clear registers may have latched or write-one-to-clear semantics not represented here. Generic read-modify-write patterns can lose diagnostic evidence or clear unrelated status.
- PASID, atomic operation, LTR, TPH, ACS, AER, and MSI registers affect PCIe protocol behavior. Bad values can appear as device-specific performance issues, DMA faults, interrupt loss, or upstream PCIe errors.
- GPU-IOV vendor-specific scheduling registers are repeated and mechanically named. A single EPF0/EPF1 offset mismatch could break only one engine scheduler or virtual-function exposure path, making failures topology- or workload-specific.
- SION credit/status registers expose live hardware flow-control state. Polling or diagnostics must tolerate asynchronous changes and avoid treating sampled counters as persistent software-owned state.

## Test Signals

- Build AMDGPU code paths that include NBIO 7.2.0 headers; compile coverage catches renamed, removed, or malformed symbols used by consumers.
- Run generated-header consistency checks: every register offset in this range should have a matching `_BASE_IDX`, all `_BASE_IDX` values should be expected for NBIO 7.2.0, and repeated EPF0/EPF1/EPF2/EPF3 standard PCIe register patterns should align.
- Cross-check this offset header against `nbio_7_2_0_sh_mask.h` and default/reset metadata so field layouts and offsets refer to the same register names.
- On supported hardware, validate PCIe enumeration, BAR sizing, MSI delivery and masking, AER reporting, LTR/TPH negotiation, PASID/ATS-related behavior where applicable, and suspend/resume register restoration.
- Exercise GPU reset paths: FLR, hot reset, function reset pulse counters, sticky reset status, D-state transitions, and full GPU reset recovery should leave PCIe configuration and NBIO status coherent.
- Exercise RAS and diagnostic paths where available: parity/error logging, virtual-wire notification, PASID/atomic/DMA error logs, and status clear paths should preserve unrelated latched state.
- For virtualization-enabled configurations, validate GPU-IOV scheduling/vendor-specific registers for EPF0 and EPF1 under virtual-function creation, reset, engine scheduling, and teardown.
- For NBIF/SION diagnostics, sample buffer status and credit registers under MMIO/DMA load and confirm counters/statuses remain plausible across power-management transitions.

### subset-b-003150: lines 9784-12207

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 9784-12207

## Purpose

This chunk is an auto-generated AMD NBIO 7.2 register-offset slice for NBIF PCI/PCIe configuration decode blocks. It exports preprocessor constants that map PCI configuration-space register names to NBIO register offsets and `BASE_IDX` selector values. The range starts inside `DEV0_EPF3`, covers complete `DEV0_EPF4` through `DEV0_EPF7` endpoint-function blocks, covers complete `DEV1_EPF0`, and begins `DEV1_EPF1`.

The header does not contain executable code, data structures, or register access helpers. Its role is to give AMDGPU and display code stable symbolic names for hardware offsets that are used with the companion NBIO 7.2 shift/mask header and the driver's register access macros.

## Public Surface In This Chunk

The public API is a dense set of `#define` macros:

- `regBIF_CFG_DEV*_EPF*_0_*` names provide word-oriented NBIO offsets for PCI config registers.
- `regBIF_CFG_DEV*_EPF*_0_*_BASE_IDX` names provide the associated register base index; every macro in this chunk uses base index `5`.

The selected range contains 2,400 `#define` lines. Its address-block boundaries are:

- Continuation of `nbio_nbif0_bif_cfg_dev0_epf3_bifcfgdecp`, whose base address is `0x10143000`; the chunk begins at `DEV0_EPF3` MSI-X, vendor-specific, AER, BAR, power-budget, DPA, ACS, PASID, ARI, TPH requester, and 64-entry TPH steering-table offsets.
- `nbio_nbif0_bif_cfg_dev0_epf4_bifcfgdecp`, base `0x10144000`.
- `nbio_nbif0_bif_cfg_dev0_epf5_bifcfgdecp`, base `0x10145000`.
- `nbio_nbif0_bif_cfg_dev0_epf6_bifcfgdecp`, base `0x10146000`.
- `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`, base `0x10147000`.
- `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`, base `0x10148000`.
- Start of `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`, base `0x10149000`; this chunk ends after the early PM/SBRN/FLADJ offsets.

## Important Register Families

For `DEV0_EPF4` through `DEV0_EPF7`, the complete repeated endpoint-function layout includes standard PCI header offsets such as vendor/device ID, command/status, revision/class-code bytes, BAR1 through BAR6, CardBus CIS pointer, subsystem adapter ID, ROM BAR, capability pointer, interrupt line/pin, min grant, and max latency. Each function then exposes PM capability offsets, PCIe capability offsets, device/link capability and control/status registers, MSI and MSI mapping offsets, MSI-X table/PBA offsets, vendor-specific enhanced capability offsets, AER status/mask/severity/control/header-log/TLP-prefix-log offsets, enhanced BAR capability/control offsets, power-budget and Dynamic Power Allocation offsets, ACS, PASID, ARI, TPH requester capability/control, and TPH steering table entries 0 through 63.

The `DEV1_EPF0` block has the same endpoint-style base PCI, PM, PCIe, MSI/MSI-X, vendor-specific, AER, BAR, power-budget, DPA, ACS, PASID, ARI, and TPH requester coverage. It additionally continues into newer PCIe link feature groups: secondary PCIe capability/list offsets, link capability/control/status 2, lane equalization controls for lanes 0-15, LTR enhanced capability offsets, data-link feature capability/status, 16 GT PHY/link capability/control/status, 16 GT parity mismatch status registers, per-lane 16 GT equalization controls, PCIe lane margining capability/status, and per-lane margining control/status for lanes 0-15.

The `DEV1_EPF1` block begins with the same standard endpoint header sequence, but this chunk only reaches through `SBRN` and `FLADJ`. Its remaining capability families are outside the selected lines and must be described by adjacent chunk research.

Several logical fields intentionally share the same offset because PCI config registers pack multiple fields into one dword or word. Examples in this chunk include vendor/device ID at the same dword, command/status at the same dword, device control/status pairs, link control/status pairs, DPA status/control, ACS capability/control, PASID capability/control, ARI capability/control, paired TPH steering table entries, 16 GT lane equalization groups, and margining lane control/status pairs.

## Control Flow And State

There is no runtime control flow in this header slice. The effective flow is compile-time substitution:

1. AMDGPU or display code includes `nbio/nbio_7_2_0_offset.h`.
2. Code chooses a `regBIF_CFG_*` offset and matching `*_BASE_IDX`.
3. The selected constants are passed to AMD register access helpers or used with companion shift/mask macros from `nbio_7_2_0_sh_mask.h`.
4. Hardware state is read, written, or decoded outside this header.

The header itself stores no state and has no persistence behavior. Persistent and externally visible state lives in GPU NBIO PCI/PCIe configuration registers. Offsets in this range can address configuration state for BAR assignment, command/status bits, power management, MSI/MSI-X routing, PCIe link controls, AER status/masks, ACS isolation, PASID/ARI behavior, TPH requester configuration, power budget/DPA controls, LTR/data-link features, 16 GT link training state, and lane margining status.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header naming convention. The offset header supplies register addresses and base indices; `nbio_7_2_0_sh_mask.h` supplies field shifts and masks for the same NBIO generation. Consumers must combine these constants with the AMDGPU register access layer and the relevant PCI/PCIe semantic rules; the preprocessor definitions do not enforce valid bit combinations, access sizes, side effects, or sequencing.

Direct include users in this tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` and DCN resource files under `drivers/gpu/drm/amd/display/dc/resource/dcn301/` and `dcn31/`. The surrounding AMDGPU code is responsible for selecting the correct NBIO generation, base index, and register access path for the ASIC. The offset names also align with other generated NBIO generation headers, but the repeated shape should not be treated as proof that offsets or capabilities are interchangeable across generations.

The semantic dependencies are the PCI and PCI Express configuration-space layouts for endpoint functions, PM capability, MSI, MSI-X, PCIe capability, AER, enhanced BAR, power budget, Dynamic Power Allocation, ACS, PASID, ARI, TPH requester, LTR, data-link feature, 16 GT PHY/link/equalization, and lane margining capabilities.

## Risks And Maintenance Notes

- The selected lines start and end mid-address-block. `DEV0_EPF3` is incomplete at the start, and `DEV1_EPF1` is incomplete at the end, so adjacent chunks are required for full per-file reconciliation.
- These generated offsets must match the exact NBIO 7.2 hardware register map. A stale or transposed offset can make driver code read the wrong PCI config dword or program the wrong endpoint function.
- The large repeated `DEV0_EPF4`-`DEV0_EPF7` blocks are review-hostile: most lines differ only by function number and offset stride. Generator drift or a single missing capability can be easy to miss.
- Many registers addressed by these macros have hardware side effects or strict access rules. Status registers may be write-one-to-clear, link controls may retrain or disable links, MSI/MSI-X controls affect interrupt delivery, and ACS/PASID/ARI settings affect isolation and addressing behavior.
- Shared-offset aliases are expected for packed PCI config fields. Consumers must use the matching shift/mask constants and access width rather than assuming each macro names a distinct storage location.
- Base index `5` is part of the generated addressing contract. Using the offset with the wrong base index or SOC register aperture can target unrelated registers.
- `DEV1_EPF0` includes 16 GT and lane margining offsets that can affect high-speed link characterization and training. Debug or test code that writes these offsets without hardware-specific sequencing risks link instability.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage for `amdgpu/nbio_v7_2.c` and DCN resource translation units that include `nbio_7_2_0_offset.h`.
- Static generated-header checks that every `regBIF_CFG_*` macro in this range has a corresponding `*_BASE_IDX` macro and that all base indices remain `5`.
- Cross-header checks that offsets here have matching field definitions in `nbio_7_2_0_sh_mask.h` for registers whose bitfields are consumed by driver code.
- Register-map sanity checks that `DEV0_EPF4` through `DEV0_EPF7` advance in the expected `0x400` offset stride and that `DEV1_EPF0`/`DEV1_EPF1` begin at `0x12000`/`0x12400`.
- Hardware dump comparison on NBIO 7.2 ASICs using AMDGPU debug register reads and PCI config-space tools such as `lspci -vvxxx`, especially for vendor/device IDs, BAR layout, capability pointers, MSI/MSI-X state, AER capability, ACS/PASID/ARI capability presence, TPH tables, LTR/data-link features, 16 GT link status, and margining capability/status.
- Error and link-management tests that exercise AER reporting, MSI/MSI-X delivery, link speed negotiation, 16 GT equalization, lane margining reads, and power-management capability decoding without touching unrelated endpoint functions.

### subset-b-003151: lines 12208-14624

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

### subset-b-003152: lines 14625-17031

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 14625-17031

## Purpose

This chunk is a generated AMD NBIO 7.2.0 register-offset slice for PCIe root-port configuration decode blocks. It contains preprocessor constants only: each `reg...` macro gives the SOC15/NBIO register offset for a PCIe configuration register, and each paired `reg..._BASE_IDX` macro identifies the register base index used by AMDGPU register access helpers.

The chunk covers the tail of `BIFPLR1_0`, full `BIFPLR2_0`, `BIFPLR3_0`, and `BIFPLR4_0` blocks, and the beginning-to-middle of `BIFPLR5_0`. It is not executable logic, but it is part of the hardware ABI used by NBIO 7.2 driver code to address PCIe capability, error handling, link-training, power-management, and lane diagnostic registers.

## Public Surface In This Chunk

The exported surface is 2,391 `#define` macros in the standard generated offset-header pattern:

- `regBIFPLR*_0_<REGISTER>`: NBIO register offset for a root-port config-space register.
- `regBIFPLR*_0_<REGISTER>_BASE_IDX`: base-index selector, consistently `5` in this slice.

The chunk starts at `regBIFPLR1_0_PCIE_LANE_7_EQUALIZATION_CNTL_BASE_IDX`, so the first visible register family is partial. It then covers `BIFPLR1_0` secondary PCIe/equalization tail, ACS, multicast, L1 PM substate, DPC, RP PIO, ESM, Data Link Feature, 16 GT PHY, margining, CCIX, and ESM lane equalization offsets through `regBIFPLR1_0_PCIE_CCIX_TRANS_CNTL`.

The full generated address blocks begin at:

- `// addressBlock: nbio_pcie0_bifplr2_cfgdecp`, base address `0x11102000`, macros `regBIFPLR2_0_*`.
- `// addressBlock: nbio_pcie0_bifplr3_cfgdecp`, base address `0x11103000`, macros `regBIFPLR3_0_*`.
- `// addressBlock: nbio_pcie0_bifplr4_cfgdecp`, base address `0x11104000`, macros `regBIFPLR4_0_*`.
- `// addressBlock: nbio_pcie0_bifplr5_cfgdecp`, base address `0x11105000`, macros `regBIFPLR5_0_*`.

The `BIFPLR5_0` block is partial in this chunk: it starts at standard PCI configuration registers and ends at `regBIFPLR5_0_LANE_9_MARGINING_LANE_STATUS_BASE_IDX`; lanes 10-15 margining and later CCIX/ESM entries continue in the next source chunk.

## Important Register Families

The complete `BIFPLR2_0`, `BIFPLR3_0`, and `BIFPLR4_0` blocks each map a bridge/root-port style PCIe configuration space. Their standard PCI header coverage includes vendor/device IDs, command/status, revision/class codes, cache-line/latency/header/BIST fields, bus numbering, IO and memory bridge windows, prefetchable window upper/lower registers, capability pointers, ROM base address, interrupt line/pin, bridge control, and vendor/adapter ID capability registers.

The PCI power, PCIe, and MSI families include PM capability/status-control, PCIe capability, device/link/slot/root capability and control/status registers, PCIe 2.0 device/link/slot extensions, MSI capability/list/control/address/data registers, SSID, and MSI map capability/address registers. These offsets allow consumers to read or program endpoint/root-port identity, interrupt routing, bridge aperture, link state, slot state, root error state, and power-management capability registers.

The extended PCIe capability families include vendor-specific capability registers, virtual channel resource registers, device serial number registers, AER status/mask/severity/capability/header-log/root-error/source-ID registers, TLP prefix logs, secondary PCIe link-control/equalization registers, ACS capability/control, multicast capability/control/address/receive/block/overlay BAR registers, L1 PM substate capability/control registers, DPC capability/control/status/source ID, RP PIO status/mask/severity/system-error/exception/header-log/prefix-log registers, ESM capability/header/status/control/capability registers, Data Link Feature capability/status, 16 GT PHY link capability/control/status/parity and lane equalization, PCIe margining port/lane registers, CCIX capability/ESM registers, and ESM 20 GT/25 GT lane equalization controls.

Per-lane families are intentionally repetitive. The slice includes 16-lane secondary equalization offsets, 16 GT equalization offsets, margining lane control/status offsets, and ESM 20 GT/25 GT equalization offsets. Several adjacent lane macros share a single dword offset because the hardware packs multiple lane fields into one register; field-level shifts and masks live in the sibling `nbio_7_2_0_sh_mask.h` header.

## Control Flow And State

There is no runtime control flow in this file. The effective flow is compile-time substitution:

1. AMDGPU NBIO 7.2 code includes `nbio_7_2_0_offset.h` and `nbio_7_2_0_sh_mask.h`.
2. A call site passes a `reg...` macro to a register helper such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, or `WREG32_PCIE_PORT`.
3. If individual fields are needed, the call site combines the address macro from this file with shift/mask macros from the companion mask header and helper macros such as `REG_SET_FIELD`.

The header stores no C state and has no persistence layer. State is the hardware state in the GPU's NBIO PCIe configuration and capability registers. Many addressed registers represent persistent or externally visible hardware state until reset or explicit driver/firmware/PCIe action: bridge windows, command bits, MSI routing, PM state, link control, link equalization, lane margining results, AER/DPC/RP PIO error status and logs, ACS isolation controls, multicast routing, L1 PM substate settings, and CCIX/ESM capability state.

## Dependencies And Integration Points

This chunk depends on the generated AMD register-header convention for SOC15/NBIO hardware. The offset header supplies addresses and base indices; `nbio_7_2_0_sh_mask.h` supplies field shifts and masks for the same register names. Callers must use both correctly: an offset macro alone says where a register lives, not which bits are safe or meaningful.

The direct driver include point found in this tree is `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, which includes both `nbio/nbio_7_2_0_offset.h` and `nbio/nbio_7_2_0_sh_mask.h`. That NBIO implementation uses the same register-access ecosystem to configure memory-controller access, doorbell apertures, interrupt handling, HDP remap registers, and PCIe/NBIO controls. This chunk's root-port constants are therefore available to NBIO 7.2 code paths even when only a subset is touched by current call sites.

Semantic dependencies are the PCI and PCI Express specifications plus AMD's NBIO 7.2 register map. Register names encode standard capabilities such as PM, MSI, PCIe capability, AER, VC, ACS, multicast, L1 PM substate, DPC, Data Link Feature, 16 GT PHY, margining, and vendor/CCIX/ESM extensions, but this header does not enforce legal ordering, access width, write-one-to-clear behavior, or hardware side effects.

## Risks And Maintenance Notes

- The chunk boundaries are not semantic boundaries. It starts in the middle of `BIFPLR1_0` lane equalization and ends in the middle of `BIFPLR5_0` margining, so adjacent chunk research is required for complete per-block coverage.
- Address and base-index macros must match the NBIO 7.2.0 hardware definition exactly. A stale or cross-generation offset can make otherwise correct field code read or write the wrong PCIe/NBIO register.
- Many names are repeated across `BIFPLR2_0`, `BIFPLR3_0`, `BIFPLR4_0`, and `BIFPLR5_0` with only address offsets changing. Generated drift or copy/paste edits are hard to review visually.
- Packed registers intentionally have multiple symbolic names at the same offset, such as vendor/device ID pairs, command/status pairs, MSI address/data aliases, DPC capability/control pairs, ESM header/status pairs, and per-lane equalization groups. Consumers must rely on the companion shift/mask header for field disambiguation.
- Error/status/log registers in AER, DPC, RP PIO, ESM, link parity, and margining families may have hardware side effects, including write-one-to-clear status or latched diagnostic state. Read-modify-write is not automatically safe just because an offset macro exists.
- Control registers for ACS, multicast, bridge apertures, MSI, L1 PM substates, link retraining/equalization, DPC, CCIX, and ESM can affect isolation, interrupt delivery, power behavior, error containment, and PCIe link stability.
- The consistent `_BASE_IDX 5` convention is part of the SOC15 address calculation contract. Mixing these offsets with helpers or base indices from another NBIO generation can silently address a different register window.

## Test Signals

Useful validation signals for this chunk are:

- Compile coverage of NBIO 7.2 translation units that include `nbio_7_2_0_offset.h`, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`.
- Static generated-header checks that every `regBIFPLR*_0_*` offset in this slice has a paired `_BASE_IDX`, that each base index remains `5`, and that complete `BIFPLR2_0` through `BIFPLR4_0` blocks retain the same register-name sequence with the expected address stride.
- Cross-header checks that register names in this offset slice have corresponding shift/mask definitions in `nbio_7_2_0_sh_mask.h` where fields are defined.
- Hardware register-dump comparison on NBIO 7.2 devices against PCI config-space views such as `lspci -vvxxx` and AMDGPU debug register reads for vendor/device IDs, class codes, bridge windows, PM/MSI/PCIe capabilities, AER/DPC state, link speed/width, ACS controls, L1 PM substate controls, and lane equalization/margining registers.
- Runtime link/error-path tests that exercise PCIe retraining, equalization, AER reporting/clearing, DPC containment, RP PIO logging, L1.1/L1.2 behavior, and margining diagnostics without modifying unrelated packed fields.

### subset-b-003153: lines 17032-19461

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 17032-19461

## Scope

This chunk covers a generated AMD NBIO 7.2.0 register offset header section. It starts in the tail of the `nbio_pcie0_bifplr5_cfgdecp` PCIe root-port capability map, then covers the complete `nbio_pcie0_bifplr6_cfgdecp` root-port configuration block, repeated per-port PCIe directory blocks `nbio_pcie0_bifp0_pciedir_p` through `nbio_pcie0_bifp6_pciedir_p`, the shared `nbio_pcie0_pciedir` block, the one-register `nbio_iohub_nb_fastreg_fastreg_cfgdec` block, and the start of `nbio_iohub_nb_misc_misc_cfgdec`.

The file is data-only C preprocessor material. This range defines 2386 `#define` constants: register-offset macros such as `regBIFPLR6_0_LINK_STATUS` and their matching `<name>_BASE_IDX` macros. It defines no functions, structs, variables, storage, locks, allocations, or executable MMIO operations.

## Purpose

This header section is the address side of the NBIO 7.2.0 hardware register ABI used by AMDGPU code. Each non-`_BASE_IDX` macro maps a symbolic NBIO/PCIe register name to a generated register offset, while each `_BASE_IDX` macro identifies the SOC15 base-index slot used by AMDGPU register helpers.

Consumers normally pair these offsets with matching shift/mask definitions from `nbio_7_2_0_sh_mask.h` and defaults from `nbio_7_2_0_default.h`. Driver code then accesses the registers through helper patterns such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE`, `WREG32_PCIE`, `REG_SET_FIELD`, and `REG_GET_FIELD`, depending on the call site and address space.

## Important Macro Families

### BIFPLR5 Tail: Margining, CCIX, and ESM

The chunk begins after the `BIFPLR5_0` register family has already started. Covered macros finish lane margining control/status for lanes 10-15, then define CCIX and ESM-related capability/control offsets:

- `regBIFPLR5_0_PCIE_CCIX_CAP_LIST`, `PCIE_CCIX_HEADER_1/2`, `PCIE_CCIX_CAP`, `PCIE_CCIX_ESM_REQD_CAP`, `PCIE_CCIX_ESM_OPTL_CAP`, `PCIE_CCIX_ESM_STATUS`, and `PCIE_CCIX_ESM_CNTL`.
- `regBIFPLR5_0_ESM_LANE_0_EQUALIZATION_CNTL_20GT` through lane 15 and the equivalent `25GT` lane equalization controls.
- `regBIFPLR5_0_PCIE_CCIX_TRANS_CAP` and `PCIE_CCIX_TRANS_CNTL`.

This is a partial family because lanes 0-9 margining and earlier BIFPLR5 capability fields live in the previous chunk.

### BIFPLR6 Root-Port Configuration Space

The `nbio_pcie0_bifplr6_cfgdecp` block begins at base address `0x11106000` and is represented by `regBIFPLR6_0_*` offsets. It mirrors a PCIe root-port configuration-space view and includes:

- Standard PCI/PCIe header fields: vendor/device ID, command/status, class/revision, cache/latency/header/BIST, bus number and bridge window registers, ROM base, interrupt fields, and bridge control.
- Power management and PCIe capability registers: `PMI_*`, `PCIE_CAP`, `DEVICE_CAP/CNTL/STATUS`, `LINK_CAP/CNTL/STATUS`, slot/root capability and status registers, plus PCIe 2 capability/status families.
- MSI, SSID, MSI map, vendor-specific, virtual-channel, device serial number, advanced error reporting, secondary PCIe, ACS, multicast, L1 PM substate, DPC, RP PIO, data-link feature, 16GT PHY, margining, CCIX, and ESM/ESM-lane equalization registers.

Many logical fields intentionally share the same DWORD offset because PCI config registers pack multiple fields into one 32-bit location. For example ID, command/status, class-code, MSI, PCIe capability, margining control/status, and CCIX header/capability macros often alias the same offset with different symbolic names.

### Repeated BIFP0-BIFP6 PCIe Port Directories

The seven `nbio_pcie0_bifp*_pciedir_p` blocks at base addresses `0x11140000` through `0x11146000` repeat an identical per-port register layout using prefixes `regBIFP0_` through `regBIFP6_`. Each block covers:

- Per-port scratch, port control, requester ID, vendor-specific, sequence/replay/ACK/NAK, TX/RX control, and skid/nop-DLLP controls.
- Posted, non-posted, and completion flow-control credit advertising, initialization, allocation, and status registers, including VC1 flow-control views.
- CCIX port controls and stacked base/limit/misc status.
- Error handling and debug registers such as `PCIE_ERR_CNTL`, physical/transaction error injection, NAK counters, captured LTR control/status, AER private uncorrectable mask, and AER private trigger.
- Link-control and training registers: `PCIE_LC_CNTL`, training, width, speed, N_FTS, CDR, lane control, bandwidth-change control, force coefficient, best equalization settings, equalization request coefficient, link-management status/mask/control, L1 PM substates, port order, and later LC control/save-restore registers.
- Strap, BCH ECC, HPGI, HCNT descriptor, performance count, fine-grain clock-gate override, and save/restore offsets.

The repeated shape is important: a caller that selects the wrong `BIFP` prefix will program a different physical PCIe port even though the register family name and relative layout look correct.

### Shared PCIe Directory and Link/Performance Diagnostics

The `nbio_pcie0_pciedir` block at base address `0x11180000` defines shared `regPCIE_*`, `regSWRST_*`, `regCPM_*`, `regSMN_*`, `regLNCNT_*`, and `regLC_*` offsets. Major groups include:

- Common PCIe control/status: reserved/scratch, RX NAK counters, `PCIE_CNTL`, `CONFIG_CNTL`, TX tracking address/control/status, master control, common AER mask, bus control, WPR control, last-TLP capture, I2C register address/data, and configuration control.
- Link-state and power-management state: `PCIE_LC_STATE6` through `STATE11`, `PCIE_LC_STATUS1/2`, `PCIE_LC_PM_CNTL`, port-order control, P-buffer/P-decoder/P-misc status, and receive L0s FTS detect.
- CCIX and SDP controls: `PCIE_TX_CCIX_CNTL0/1`, `PCIE_TX_CCIX_PORT_MAP`, `PCIE_TX_CCIX_ERR_CTL`, `PCIE_RX_CCIX_CTL0`, `PCIE_RX_AD`, `PCIE_SDP_CTRL`, and SDP slave attribute controls for SWUS and RC paths.
- Performance counters across TXCLK and SCLK domains: `PCIE_PERF_COUNT_CNTL`, `PCIE_PERF_CNTL_TXCLK1..4`, `PCIE_PERF_COUNT0/1_TXCLK1..4`, `PCIE_PERF_CNTL_SCLK1/2`, `PCIE_PERF_COUNT0/1_SCLK1/2`, and event port-select registers.
- Strap and PRBS diagnostics: `PCIE_STRAP_*`, `PCIE_PRBS_CLR`, status, freerun, misc, user pattern, low/high bit counts, and per-lane error counters `PCIE_PRBS_ERRCNT_0..15`.
- Software reset, clock/power management, SMN aperture IDs, lane-count controls, programmable master/slave controls, CPM split/extension controls, RX margin settings, and presence-detect selection.

These offsets are used for link bring-up, low-level diagnostics, power/clock sequencing, PRBS link tests, and reset control.

### IOHUB Fastreg and Miscellaneous NB Registers

The `nbio_iohub_nb_fastreg_fastreg_cfgdec` block contains `regFASTREG_APERTURE` at base address `0x13b07000`.

The next block, `nbio_iohub_nb_misc_misc_cfgdec`, starts at base address `0x13b10000` and this chunk covers its first misc registers:

- LCLK deep-sleep masking and software interrupt routing/control: `regNBIO_LCLK_DS_MASK`, `regSB_LOCATION`, `regSW_US_LOCATION`, `regSW_NMI_CNTL`, `regSW_SMI_CNTL`, `regSW_SCI_CNTL`, `regAPML_SW_STATUS`, `regSW_GIC_SPI_CNTL`, and `regSW_SYNCFLOOD_CNTL`.
- CAM target index/data address and mask registers: `regCAM_CONTROL`, `regCAM_TARGET_INDEX_*`, and `regCAM_TARGET_DATA_*`.
- Posted and non-posted DMA dropped-log lower/upper registers.
- PCIe VDM controls and crossbar stall controls for ports 0-6.
- Fastreg base-address programming registers: `regFASTREG_BASE_ADDR_LO/HI` and `regFASTREGCNTL_BASE_ADDR_LO/HI`.

The chunk ends before scratch/trap request/response registers that continue the same misc block in the following lines.

## Control Flow and State Behavior

There is no runtime control flow in this header. Its effect is compile-time: symbolic constants determine which MMIO/config-space offsets AMDGPU code reads or writes.

The state described by this chunk is hardware state, not software state in the header. Durable configuration includes PCIe command/status and bridge aperture registers, root-port capabilities and controls, MSI mapping, virtual-channel controls, ACS/multicast/L1 PM/DPC settings, lane equalization and margining controls, per-port flow-control credits, link training policy, clock-gating overrides, reset controls, SMN aperture IDs, fastreg base addresses, and CAM target mappings.

Other offsets expose volatile or sticky hardware status: link status, AER/DPC/RP PIO error status and logs, lane error status, margining status, CCIX/ESM status, TX/RX replay and NAK counters, captured LTR and last-TLP data, PRBS bit/error counters, software reset command status, DMA dropped logs, and crossbar stall state. Some registers are command-like, including software reset command/control registers, PRBS clear controls, error-injection registers, AER/DPC clear/status paths, and margining control/status windows. The header does not encode ordering, polling, timeout, or clear-on-write semantics; those must come from the owning driver code and hardware specification.

## Dependencies and Integration Points

This chunk depends on the generated NBIO 7.2.0 header set:

- `nbio_7_2_0_sh_mask.h` supplies field positions and masks for the offsets named here.
- `nbio_7_2_0_default.h` supplies generated reset/default values where present.
- SOC15 and AMDGPU register helpers consume the `<register>` and `<register>_BASE_IDX` convention to form MMIO addresses for NBIO instances.

Primary integration points are AMDGPU NBIO, PCIe, reset, RAS, and low-level diagnostics code. Typical consumers include ASIC-specific NBIO initialization and suspend/resume paths, PCIe link-speed/link-width management, ASPM/L1 PM handling, AER/DPC error reporting, SR-IOV or partitioning code that must distinguish ports and requester IDs, and debug tooling for PRBS, flow-control, replay/NAK, last-TLP, lane margining, and equalization. Because this is an offset header, most call sites include it indirectly through NBIO 7.2.0 register header aggregation rather than manipulating the file directly.

The chunk also integrates with adjacent generated chunks. The BIFPLR5 family is incomplete at the start, and the IOHUB misc block is incomplete at the end. The final per-file reconciliation should stitch these boundaries before treating either address block as fully documented.

## Risks

- Offset drift is high impact. An incorrect register offset or base index can send an otherwise valid read/write to the wrong NBIO or PCIe register, causing link training failure, bad bridge apertures, broken interrupts, lost AER/DPC information, hangs, or misleading diagnostics.
- Packed PCI config registers create deliberate aliasing. Multiple symbolic names often share a DWORD offset; consumers must use the matching shift/mask header instead of assuming each macro names an independent register.
- The BIFP0-BIFP6 blocks are mechanically repetitive. Copying code between ports with the wrong prefix can silently target the wrong physical PCIe port.
- Link-control, equalization, margining, and speed/width registers are sequencing-sensitive. Writes outside the expected training/retraining flow can destabilize the PCIe link.
- Error-injection, PRBS, AER, DPC, and RP PIO registers are diagnostic or fault-management surfaces. Leaving injected-error or clear/status bits in the wrong state can hide real link faults or create false ones.
- Flow-control credit and VC/CCIX controls can affect traffic ordering and forward progress. Incorrect programming can cause packet stalls, replay storms, or CCIX/VC interoperability failures.
- Reset and clock/power management registers are broad in blast radius. `SWRST_*`, `CPM_*`, lane-count, LCLK, and fine-grain clock-gate override registers must stay coordinated with NBIO reset and power-management policy.
- Fastreg, CAM, and SMN aperture registers affect address routing or indirect register access. Incorrect base/mask programming can route transactions incorrectly or make diagnostic windows point at the wrong target.
- Chunk boundaries split families. The BIFPLR5 start is partial, and the misc block continues after `FASTREGCNTL_BASE_ADDR_HI`; conclusions about those blocks need adjacent chunks.

## Test and Validation Signals

Useful validation is mostly build, hardware bring-up, and PCIe diagnostics coverage:

- Build AMDGPU code paths that include the NBIO 7.2.0 offset/mask/default headers; this catches missing, renamed, or syntactically broken generated macros.
- PCIe enumeration and bridge-window tests should validate standard BIFPLR6 config-space offsets for vendor/device ID, class code, command/status, bus numbers, BAR/ROM/interrupt fields, and capability-list traversal.
- Link bring-up and retraining tests should cover BIFP link-control, link-width, speed, N_FTS, CDR, equalization, margining, L1 PM substate, and lane-status registers across ports 0-6.
- Error-path validation should exercise AER, DPC, RP PIO, lane-error, replay/NAK counters, captured LTR, and last-TLP logging, including status clear behavior.
- PRBS and performance-counter diagnostics should verify shared `PCIE_PRBS_*`, per-lane error counters, and TXCLK/SCLK performance counters produce expected counts during controlled link tests.
- Reset and suspend/resume testing should exercise `SWRST_*`, `CPM_*`, LCLK deep-sleep masks, fine-grain clock-gating overrides, and save/restore registers without leaving links wedged or counters stale.
- Multi-port systems should verify that operations against `regBIFP0_*` through `regBIFP6_*` affect only the intended physical port.
- IOHUB misc validation should confirm fastreg aperture/base programming, CAM target mapping, dropped-DMA logs, VDM controls, and crossbar stall registers decode consistently with hardware events.

## Unresolved Cross-Chunk References

Line 17032 starts in the middle of the BIFPLR5 lane-margining family; lanes 0-9 and earlier BIFPLR5 PCIe capability registers are in the previous chunk. Line 19461 stops after `regFASTREGCNTL_BASE_ADDR_HI`, while the same `nbio_iohub_nb_misc_misc_cfgdec` block continues immediately afterward with scratch and trap request/response registers. The merge/reconciliation lane should connect both boundaries when producing the final per-file research document.

### subset-b-003154: lines 19462-21877

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 19462-21877

## Chunk Scope

- Work item: `subset-b-003154`
- Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h`, lines 19462-21877
- Parent file role: generated AMDGPU NBIO 7.2.0 register offset map used by SOC15 register access macros.
- Chunk shape: 2,348 preprocessor definitions, representing 1,174 register symbols plus one paired `*_BASE_IDX` definition for each symbol. Every `*_BASE_IDX` in this span is `5`.

## Purpose

This chunk contributes register-offset constants for the NBIO 7.2.0 block used by AMD GPU kernel code. It does not implement runtime behavior directly. Its job is to provide stable symbolic register names and base-index metadata for code that calls macros such as `SOC15_REG_OFFSET(NBIO, instance, reg...)`, `RREG32_SOC15(...)`, `WREG32_SOC15(...)`, and PCIe-port register helpers.

The covered registers are concentrated in debug/trap access, RAS and parity handling, NBIF/BIF/RCC virtualization and doorbell routing, GDC doorbell ranges, and two PCIe logical-root-port configuration spaces (`BIFPLR0_1` and `BIFPLR1_1`). These definitions are consumed indirectly by NBIO support code such as `amdgpu/nbio_v7_2.c` and display resource files that include this header for NBIO 7.2.0 hardware.

## Major Register Families In This Chunk

- Lines 19462-19812 continue a previous address block and define `SCRATCH_4`, `SCRATCH_5`, trap request/response registers, `TRAP0` through `TRAP15` match registers, bridge/security status registers, sideband bridge controls, and MCA SMN interrupt request registers. The chunk begins after the address-block marker from the prior chunk, so the merge pass should retain the previous block context.
- Lines 19814-19815 mark `nbio_iohub_nb_security_security_cfgdec` at base `0x13b18000`, but this chunk shows only the marker and no register macros under it before the next block.
- Lines 19818-20115 define `nbio_iohub_nb_rascfg_ras_cfgdec` at base `0x13b20000`. This section includes parity controls, global RAS status, uncorrectable/correctable/UCP parity status and counters for groups 0-7, miscellaneous RAS controls, per-event action-control registers for parity and PCIe/NBIF port error classes, sync flood/NMI status, poison status/masks/severity, and APML status/control/trigger registers.
- Lines 20118-20125 define PF2 indexed MMIO registers for `nbio_nbif0_bif_bx_pf_SYSPFVFDEC`, including `BIF_BX_PF2_MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`.
- Lines 20128-20223 define `nbio_nbif0_bif_bx_SYSDEC`, including PF2 PCIe index/data windows and SBIOS/BIOS scratch registers.
- Lines 20226-20227 mark `nbio_nbif0_syshub_mmreg_syshubdec`, but no register macros appear in this chunk under that marker.
- Lines 20230-20425 cover several RCC strap, endpoint, downstream, and downstream-port decode blocks. These include reset, PLL, hotplug, slot capability, link control, lane count, transmitter/rx, strap, LTR, and PCIe error-control registers for device 0 pathing.
- Lines 20428-20547 cover RCC endpoint PF/VF decode and device decode registers. Important groups include duplicated PF/VF aliases for error logs, doorbell aperture enable, configured memory size, IOV function identifiers, GPU IOV region/HostVM controls, console IOV controls, peer register and framebuffer offsets, bus-number lists, requester-id restore, LTR switch controls, and multi-host arbitration.
- Lines 20550-20695 define `nbio_nbif0_bif_bx_BIFDEC1`. This is a dense NBIF/BIF control group: straps, indirect-access control, bus and reset controls, interrupts, doorbell and framebuffer enables, BACO timing controls, NBIF graphics address LUT entries 0-15, VF register-write/doorbell/framebuffer enable and status registers, HDP flush remap controls, BIF ring-buffer controls, mailbox index, GPUIOV config sizes, pad controls, PCIe parameter save/restore, and S5 memory power controls.
- Lines 20698-20751 define PF2-specific BIF/PF/VF registers, including BME status, atomic error log, doorbell self-ring GPA aperture base/control, HDP coherency flush/invalidate controls, GPU HDP request/done registers, transaction-pending status, graphics address LUT bypass, mailbox transfer/receive buffers, mailbox control/interrupt control, and VM/HV mailbox.
- Lines 20754-20817 define GDC1 registers. They include SDP/SHUB/MP4SDP controls, MGCG controls, doorbell status, and doorbell range registers for SDMA, IH, VCN, RLC, UVD, VCE, ACP, and DSC engines.
- Lines 20820-20923 define a second RCC endpoint PF/VF decode set, including `RCC_DEV0_EPF0_2_*` error logs, command memory region, more IOV region/HostVM controls, and per-function doorbell aperture config/memory size/function identifier aliases.
- Lines 20926-21471 define `nbio_pcie0_bifplr0_cfgdecp`, the first large PCIe logical-root-port configuration group. It maps standard and extended PCIe config-space-like registers: device/vendor IDs, command/status, BARs, capabilities, link control/status, bridge controls, MSI/MSI-X, PCIe capability fields, AER status/masks/severity/logs, root error command/status, secondary capabilities, lane equalization, ACS, multicast, L1 PM substates, DPC, RP PIO error reporting/logging, ESM, data-link feature, 16 GT PHY/link status/equalization, margining, CCIX/ESM capabilities, and 20 GT ESM lane equalization.
- Lines 21474-21877 begin `nbio_pcie0_bifplr1_cfgdecp`, a second PCIe logical-root-port configuration group with the same general structure as `BIFPLR0_1`. This chunk covers the first part through 16 GT link/equalization and the start of PCIe margining lane controls. It ends mid-table at `BIFPLR1_1_LANE_1_MARGINING_LANE_CNTL_BASE_IDX`; remaining lane margining status/control definitions continue in chunk 10.

## Important APIs, Types, And Symbols

There are no C functions, structs, enums, or storage definitions in this chunk. The public interface is entirely preprocessor symbols:

- Register-offset macros such as `regTRAP_STATUS`, `regRAS_GLOBAL_STATUS_LO`, `regBIF_BX2_BIF_DOORBELL_CNTL`, `regBIF_BX_PF2_GPU_HDP_FLUSH_REQ`, `regGDC1_BIF_IH_DOORBELL_RANGE`, `regBIFPLR0_1_PCIE_UNCORR_ERR_STATUS`, and `regBIFPLR1_1_LINK_STATUS_16GT`.
- Paired base-index macros such as `regTRAP_STATUS_BASE_IDX` and `regBIFPLR1_1_LINK_STATUS_16GT_BASE_IDX`, all set to `5` in this chunk. SOC15 access code uses the base index to select the proper register base for the IP block/version.
- Indexed/indirect access registers (`*_MM_INDEX`, `*_MM_DATA`, `*_PCIE_INDEX`, `*_PCIE_DATA`) that let runtime code reach subregister spaces through index/data windows.
- Doorbell routing and virtualization registers (`*_DOORBELL_*`, `*_GPUIOV_*`, `*_VF_*`, `*_MAILBOX_*`) that are central to queue notification, SR-IOV/MxGPU-style partitioning, and PF/VF communication.
- PCIe configuration-space aliases under `BIFPLR0_1` and `BIFPLR1_1`, which expose link training, AER, DPC, ACS, L1 PM substates, multicast, ESM, PHY 16 GT, 20 GT, and margining features.

## Control Flow

This header has no executable control flow. Runtime flow is created by users of the symbols:

1. Driver code selects a symbolic register name for a particular NBIO operation.
2. SOC15 helper macros combine the register offset macro, the corresponding `*_BASE_IDX`, IP block identity, and instance number into an MMIO address.
3. The driver reads, writes, or polls that address through AMDGPU register access helpers.

The chunk's control-flow significance is therefore data-driven. For example, NBIO code that configures HDP flush, doorbell range, interrupt routing, or PCIe link behavior depends on these offset values resolving to the intended hardware registers.

## State And Persistence Behavior

The file itself has no mutable process state and does not persist data. The registers it names are hardware state:

- Trap, scratch, mailbox, and response registers can hold transient debug or firmware/driver communication state.
- RAS/parity/poison/AER/DPC/RP PIO status registers reflect hardware error state and may be sticky until cleared by driver policy.
- Doorbell aperture/range, VF enable, GPUIOV, HostVM, peer offset, and mailbox-control registers affect live device routing and virtualization state.
- PCIe link, lane equalization, L1 PM substate, 16 GT/20 GT, and margining registers reflect or influence physical/link-layer state.
- BACO, S5 memory power, reset, pad, and save/restore controls participate in power-management and reset persistence across low-power or resume paths.

Because this is a generated offset header, persistence risk is not in the source file itself. Risk lies in stale or mismatched offsets causing the driver to mutate the wrong hardware state.

## Dependencies And Integration Points

- Included by `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, where NBIO 7.2.0-specific helper functions use SOC15 read/write macros for doorbells, HDP flush, interrupts, PCIe controls, and related operations.
- Included by display resource code under `drivers/gpu/drm/amd/display/dc/resource/dcn301/` and `dcn31/`, giving display code access to NBIO 7.2.0 offsets when resource logic needs NBIO registers.
- Depends on the AMDGPU SOC15 register-base machinery outside this file. The numeric `*_BASE_IDX` values are meaningful only when paired with the generated IP-base tables and access macros.
- Integrates with adjacent generated headers for bitfield masks/shifts. Offset headers identify register locations; field headers are needed to safely manipulate individual bits.
- Related NBIO offset headers, such as `nbio_7_7_0_offset.h`, `nbio_7_9_0_offset.h`, and `nbio_7_11_0_offset.h`, define similar names with different offsets or base indices. Porting code across ASIC generations must use the matching header/version.

## Risks And Edge Cases

- The chunk starts in an already-open address block and ends mid-way through the `BIFPLR1_1` margining lane definitions. The merge lane must preserve cross-chunk continuity rather than treating these as independent complete blocks.
- All base indices are `5` here, but similar names in nearby NBIO versions can use different base indices or numeric offsets. Accidental include/version drift can compile cleanly while targeting the wrong MMIO address.
- Several names intentionally alias the same offset, such as capability/control pairs, per-lane grouped equalization registers, PF/VF duplicate aliases, and status/control pairs sharing DWORDs. Automated de-duplication would be unsafe because the aliases document different field views of the same register.
- PCIe logical-root-port groups `BIFPLR0_1` and `BIFPLR1_1` are large and repetitive. Copy/paste or generation errors in lane numbering, offset progression, or base index would affect link training, AER/DPC reporting, margining, and power-management behavior.
- RAS and poison registers are error-handling critical. Wrong offsets could mask, misclassify, or fail to clear hardware errors, leading to missed fatal events or noisy false positives.
- Doorbell and GPUIOV registers affect queue notification and virtualization isolation. Wrong offsets can break PF/VF separation, mailbox communication, or doorbell routing.
- Some address-block comments have no visible register definitions in this exact chunk. That is expected for generated files but matters for documentation synthesis so empty markers are not overinterpreted as implemented control paths.

## Test And Validation Signals

- Build coverage: compiling AMDGPU with NBIO 7.2.0 support verifies that all referenced symbols from this header resolve and that include ordering is intact.
- Static consistency checks: generated offset validation should confirm every `reg*` symbol has a matching `reg*_BASE_IDX`, every base index in this span is expected to be `5`, and aliased offsets are intentional rather than accidental duplicates.
- Runtime smoke tests on matching ASICs: driver probe, suspend/resume, BACO entry/exit, reset handling, and display bring-up exercise many NBIO register paths.
- Doorbell tests: SDMA/IH/VCN/RLC queue operation, interrupt delivery, and VF/PF mailbox paths exercise GDC/BIF/RCC doorbell and mailbox registers.
- Error-path tests: PCIe AER/DPC injection, poison propagation, parity/RAS event handling, and NMI/sync-flood reporting validate that status, mask, severity, and action-control offsets match hardware.
- PCIe link tests: link speed negotiation, L1 PM substates, 16 GT status, lane equalization, and margining diagnostics are useful signals for the `BIFPLR0_1` and `BIFPLR1_1` register groups.
- Cross-version regression checks: compare generated values for shared symbol families across NBIO 7.2.0, 7.7.0, 7.9.0, and 7.11.0 to catch accidental use of another ASIC generation's offsets.

## Notes For Merge/Reconciliation

- This is chunk 9 of 14 for `nbio_7_2_0_offset.h`.
- The chunk begins at line 19462 with `SCRATCH_4` and `SCRATCH_5`, continuing a block whose address-block comment appears in the previous chunk.
- The chunk ends at line 21877 before the `BIFPLR1_1` PCIe margining lane table is complete; chunk 10 should continue with lane 1 status and subsequent lane margining definitions.
- No final per-file report should be produced from this chunk alone. The later merge lane should synthesize the whole `nbio_7_2_0_offset.h` report from all 14 chunk reports.

### subset-b-003155: lines 21878-24223

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 21878-24223

## Scope

This chunk is a generated AMDGPU NBIO 7.2 offset-header segment for PCIe root-port/link register windows named `BIFPLR*_1`. It contains address constants and matching `_BASE_IDX` constants only. There are no functions, structs, enums, variables, locks, allocations, executable statements, or local algorithms in this range.

The range starts in the tail of the `BIFPLR1_1` block at lane-margining lane 1, covers the complete `nbio_pcie0_bifplr2_cfgdecp`, `nbio_pcie0_bifplr3_cfgdecp`, `nbio_pcie0_bifplr4_cfgdecp`, and `nbio_pcie0_bifplr5_cfgdecp` blocks, and then enters the `nbio_pcie0_bifplr6_cfgdecp` block through `BIFPLR6_1_STATUS`. The address-block comments identify base addresses `0xfffe0000b000`, `0xfffe0000c000`, `0xfffe0000d000`, `0xfffe0000e000`, and `0xfffe0000f000` for BIFPLR2 through BIFPLR6 respectively. All macros in this chunk use NBIO base index `5`.

Although this repository mirror is under `sources/distributed-fs/ceph-client`, this source file is AMD GPU hardware metadata. It does not implement Ceph or distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_offset.h` is the address half of AMD's generated NBIO 7.2 register interface. The macros in this chunk map PCI/PCIe configuration-space style registers for NBIO PCIe root-port/link blocks to SOC15 register offsets. The generated convention is:

- `regBIFPLR<n>_1_<REGISTER>` gives the MMIO/config decode address used by AMDGPU register helpers.
- `regBIFPLR<n>_1_<REGISTER>_BASE_IDX` gives the SOC15 base-index selector, here always `5`.

The chunk's address values span roughly `0x3fff7bfc2913` through `0x3fff7bfc3c01`. Many logical PCI config fields share a dword address, such as vendor/device ID, command/status, class-code bytes, device/status controls, link/status controls, slot controls, root capability/status, MSI data fields, and CCIX headers. That aliasing is expected because the offset header names subregister fields that occupy portions of the same 32-bit config-space dword; the companion shift/mask header defines the actual bit positions.

## Important Macro Families

The `BIFPLR1_1` tail in this chunk covers the end of one root-port/link register block:

- Per-lane PCIe margining control and status for lanes 1 through 15, continuing from lane 0 in the prior chunk.
- The PCIe margining enhanced-capability tail is followed by CCIX capability registers: `PCIE_CCIX_CAP_LIST`, `PCIE_CCIX_HEADER_1`, `PCIE_CCIX_HEADER_2`, `PCIE_CCIX_CAP`, ESM required/optional capability, ESM status/control, 20 GT/s and 25 GT/s ESM lane equalization controls for lanes 0 through 15, and CCIX transport capability/control.

The `BIFPLR2_1`, `BIFPLR3_1`, `BIFPLR4_1`, and `BIFPLR5_1` blocks are complete and repeat the same generated register layout:

- Standard PCI bridge/header fields: `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, `STATUS`, revision/class-code fields, cache-line/latency/header/BIST fields, subordinate bus and I/O/memory/prefetchable window limit registers, capability pointer, ROM base, interrupt line/pin, bridge control, vendor capability, and adapter ID write field.
- Power-management and PCIe capability registers: `PMI_CAP_LIST`, `PMI_CAP`, `PMI_STATUS_CNTL`, `PCIE_CAP_LIST`, `PCIE_CAP`, device capability/control/status, link capability/control/status, slot capability/control/status, root control/capability/status, and the PCIe 2.0 device/link/slot capability/control/status 2 registers.
- Interrupt and subsystem capability registers: MSI capability list/control/message address/data fields, subsystem ID capability, and MSI map capability.
- PCIe extended capabilities: vendor-specific enhanced capability, virtual channel capability/control/status/resource registers, device serial number, Advanced Error Reporting status/mask/severity/capability/header-log/root-error/source-ID/TLP-prefix-log registers, and secondary PCIe extended capability registers.
- Link-management and containment features: link control 3, lane error status, per-lane equalization controls for lanes 0 through 15, ACS capability/control, multicast capability/control/address/receive/block/overlay registers, L1 PM substate capability/control, DPC capability/control/status/error-source, and RP PIO status/mask/severity/system-error/exception/header-log/prefix-log registers.
- Extended-speed and protocol features: ESM capability/status/control/capability registers, data-link feature capability/status, 16 GT/s PHY capability/control/status/local and RTM parity mismatch registers, 16 GT/s per-lane equalization controls, PCIe margining enhanced capability with per-lane control/status, and CCIX/ESM/transport capability and control registers.

The `BIFPLR6_1` prefix begins the next block and includes only `VENDOR_ID`, `DEVICE_ID`, `COMMAND`, and `STATUS` in this chunk. Adjacent chunks are required before treating the BIFPLR6 register block as complete.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public interface is the generated preprocessor macro namespace. Each address macro is an untyped integer literal, and each `_BASE_IDX` macro is the literal base index used by SOC15 register-offset construction.

Consumers combine these constants with AMDGPU register helpers and the sibling shift/mask header:

- `nbio_7_2_0_sh_mask.h` supplies field-level `__SHIFT` and `_MASK` definitions for the same `BIFPLR*_1_*` register names.
- `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, `REG_GET_FIELD`, and `REG_SET_FIELD` are the normal AMDGPU helper layer used around generated NBIO register metadata.
- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes both this offset header and `nbio_7_2_0_sh_mask.h`; display resource files for DCN 3.0.1 and DCN 3.1 also include this offset header for NBIO address integration.

This specific `BIFPLR*_1` chunk is mostly metadata for PCIe root-port/link configuration windows. Direct hand-written C references to these exact macro names are not prominent in the mirrored tree, but the macros remain part of the generated ABI consumed by AMDGPU register-access code and by any generated or diagnostic code that addresses these NBIO config windows.

## Control Flow

This header has no runtime control flow. Its effect is compile-time substitution:

1. An AMDGPU translation unit includes `nbio_7_2_0_offset.h`.
2. Driver or generated code selects a `regBIFPLR*_1_*` address macro and its base index.
3. The SOC15/PCIe-port helper computes the actual MMIO address for the selected NBIO instance.
4. The caller reads, writes, or read-modify-writes the register, using `nbio_7_2_0_sh_mask.h` when it needs individual fields.
5. PCIe hardware interprets the resulting root-port, link, error-reporting, lane-training, margining, power-management, or CCIX/ESM state.

The register names imply hardware flows outside this file: PCI bridge-window programming, link training and equalization, MSI setup, root-port error reporting, AER/DPC logging and clearing, L1 substate power management, ACS isolation, multicast routing, PCIe margining, 16 GT/s parity monitoring, and CCIX/ESM transport negotiation. The header itself imposes no sequencing or validation.

## State And Persistence Behavior

The header owns no state and persists nothing. It describes hardware-visible state in NBIO 7.2 PCIe configuration/register windows. Persistence depends on GPU reset domains, PCI bus reset, function reset, firmware or BIOS initialization, suspend/resume save-restore, and explicit driver writes.

The represented hardware state includes:

- PCI bridge identity, command/status, class-code, bus numbering, I/O and memory aperture windows, prefetchable aperture windows, ROM base, interrupt routing, and bridge-control bits.
- Power-management status/control and PCIe device/link/slot/root capability/control/status registers.
- MSI routing metadata and subsystem/vendor capability data.
- Virtual channel resources, AER status/mask/severity/header logs/root-error state, secondary PCIe status, ACS control, multicast routing, L1 PM substates, DPC containment and RP PIO logs.
- Per-lane equalization, lane error status, 16 GT/s parity mismatch status, lane margining control/status, CCIX capability and ESM/transport state.

Some of those registers are read-only capabilities, some are status or sticky error logs, some are write-one-to-clear status registers, and some are writable controls. The offset macros do not encode access permissions, reset values, side effects, or whether read-modify-write is safe.

## Dependencies And Integration Points

The chunk depends on AMD's generated NBIO 7.2 register database and must remain synchronized with related generated files in `drivers/gpu/drm/amd/include/asic_reg/nbio/`:

- `nbio_7_2_0_sh_mask.h` provides field masks and shifts for these address names.
- Other NBIO 7.2 generated headers, where present, provide related default/reset or instance metadata.
- `amdgpu/nbio_v7_2.c` is the primary NBIO 7.2 driver integration point and includes this header for register access across NBIO initialization, revision detection, memory-controller access, doorbell aperture setup, interrupt handling, HDP flush, and related NBIO operations.
- `display/dc/resource/dcn301/dcn301_resource.c` and `display/dc/resource/dcn31/dcn31_resource.c` include this header to share NBIO offsets with DC resource setup on ASICs using NBIO 7.2-era register maps.

Semantic dependencies are the PCI and PCI Express specifications for bridge configuration headers, PCIe capability structures, MSI, AER, virtual channels, ACS, L1 PM substates, DPC, lane equalization, lane margining, data-link feature registers, and high-speed link training. CCIX/ESM register naming also depends on the corresponding AMD hardware register specification and protocol capability layout.

## Risks And Edge Cases

- The chunk starts and ends mid-block. BIFPLR1 and BIFPLR6 must be reconciled with adjacent chunks before whole-file reports claim full coverage of those blocks.
- Generated address drift can compile cleanly but route reads and writes to the wrong NBIO config dword. For bridge-style registers this can corrupt bus windows, interrupt state, link controls, AER/DPC logs, or lane-training controls.
- Multiple logical names intentionally share one dword offset. Treating aliases such as command/status, device/status control, link/status control, MSI message data, or CCIX header/capability as independent 32-bit registers can clobber neighboring fields unless callers use the matching masks and preserve unrelated bits.
- All entries use base index `5`. A wrong base index would be a systemic integration fault even if the literal register offsets look plausible.
- Status and error-reporting registers can have write-one-to-clear or sticky semantics. The address header cannot tell callers which fields are safe for blind writes or generic read-modify-write operations.
- AER, DPC, RP PIO, ACS, multicast, L1 PM, and lane-equalization registers affect reliability, isolation, power behavior, and link stability. Misprogramming can appear only on specific platforms, link widths, speeds, resets, or error conditions.
- Per-lane equalization and margining addresses are heavily repetitive. Copy or generation errors that affect only one lane or one `BIFPLR` instance are easy to miss in review and may surface only with particular board routing or degraded links.
- CCIX/ESM and 20/25 GT/s controls may be unused on many systems, so stale or incorrect offsets can evade normal boot testing.

## Test Signals

- Build AMDGPU with NBIO 7.2 support enabled so includes from `nbio_v7_2.c`, DCN 3.0.1, and DCN 3.1 resource code catch missing or renamed macros.
- Run generated-header consistency checks: each non-`_BASE_IDX` macro in this range should have a matching `_BASE_IDX`, every `_BASE_IDX` should be `5`, and repeated `BIFPLR2_1` through `BIFPLR5_1` register families should match except for the expected address stride.
- Cross-check this offset chunk against `nbio_7_2_0_sh_mask.h` so each covered register name has corresponding field definitions where field access is expected.
- On NBIO 7.2 hardware, compare decoded BIFPLR PCIe configuration space with PCI core dumps, `lspci -vvxxx`, AMDGPU debugfs/register dumps, or vendor diagnostics for vendor/device IDs, bridge windows, PM state, link capabilities/status, MSI state, AER/DPC logs, ACS state, L1 PM substate registers, lane equalization, lane margining, and CCIX/ESM capability registers.
- Exercise suspend/resume, GPU reset, PCI bus reset or retraining, MSI enable/disable, AER/DPC error paths, and link-speed changes to confirm callers preserve reserved bits and restore expected NBIO config state.
- For lane-specific changes, test multiple link widths and degraded-width scenarios because lane 0-only testing will not cover the repeated lane 1 through 15 address families in this chunk.

### subset-b-003156: lines 24224-26565

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

### subset-b-003157: lines 26566-28914

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

### subset-b-003158: lines 28915-31260

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 28915-31260

## Scope

This chunk is a generated AMDGPU NBIO 7.2.0 register-offset header segment. It contains 2,326 `#define` constants for BIF PCI/PCIe configuration-space register offsets and companion `_BASE_IDX` values. There are no functions, structs, enums, variables, allocations, locks, persistence hooks, or executable control flow in this range.

The range starts inside the `DEV0_EPF6_1` endpoint-function block at `LINK_CAP2`/`LINK_CNTL2`, covers the tail of that function, covers complete blocks for `DEV0_EPF7_1`, `DEV1_EPF0_1`, `DEV1_EPF1_1`, and `DEV2_EPF0_1`, then enters `DEV2_EPF1_1` through `PCIE_HDR_LOG1`. The visible address blocks and base addresses are:

- `nbio_nbif0_bif_cfg_dev0_epf7_bifcfgdecp`, base `0xfffe12107000`.
- `nbio_nbif0_bif_cfg_dev1_epf0_bifcfgdecp`, base `0xfffe12300000`.
- `nbio_nbif0_bif_cfg_dev1_epf1_bifcfgdecp`, base `0xfffe12301000`.
- `nbio_nbif0_bif_cfg_dev2_epf0_bifcfgdecp`, base `0xfffe12500000`.
- `nbio_nbif0_bif_cfg_dev2_epf1_bifcfgdecp`, base `0xfffe12501000`.

Although the repository path is under a `ceph-client` mirror, this file is AMD GPU hardware metadata and has no direct distributed-filesystem behavior.

## Purpose

`nbio_7_2_0_offset.h` is the address half of AMD's generated NBIO 7.2 register interface. Each public macro named `regBIF_CFG_DEV*_EPF*_1_*` maps a PCI/PCIe configuration register name to the encoded NBIO register offset used by AMDGPU register access helpers. Each adjacent `reg..._BASE_IDX` macro identifies the NBIO base-index slot; every macro in this chunk uses base index `5`.

The chunk describes PCIe endpoint-function configuration spaces for devices 0, 1, and 2. The covered registers include standard PCI config header fields, power-management and PCIe capability registers, MSI/MSI-X state, vendor-specific and Advanced Error Reporting capabilities, BAR enhanced capability registers, power-budget and Dynamic Power Allocation registers, ACS/PASID/ARI/TPH metadata, and lane-margining control/status registers for EPF0 blocks.

The generated offsets do not encode field positions, reset defaults, access permissions, register width, write-one-to-clear behavior, or legal programming sequences. Field decoding and composition depend on the matching `nbio_7_2_0_sh_mask.h` header and AMDGPU register helpers.

## Important Macro Families

The `DEV0_EPF6_1` tail starts at PCIe capability version 2 and interrupt capability state: `DEVICE_CAP2`, `DEVICE_CNTL2`, `DEVICE_STATUS2`, `LINK_CAP2`, `LINK_CNTL2`, `LINK_STATUS2`, MSI/MSI-X registers, vendor-specific enhanced capability registers, AER status/mask/severity/log registers, BAR enhanced capability registers, power-budgeting, DPA, ACS, PASID, ARI, and the full `PCIE_TPH_ST_TABLE_0` through `PCIE_TPH_ST_TABLE_63` range. This block is partial because its standard PCI header and early PCIe capability registers are in the preceding chunk.

`DEV0_EPF7_1` and `DEV1_EPF1_1` are complete endpoint-function blocks in this range. They define standard type-0 PCI config registers such as vendor/device IDs, command/status, revision/class-code fields, cache-line/latency/header/BIST, BAR1-BAR6, adapter ID, ROM base, capability pointer, interrupt line/pin, min grant, and max latency. They then repeat the power-management, PCIe capability, MSI/MSI-X, vendor-specific, AER, BAR sizing, power-budget, DPA, ACS, PASID, ARI, and TPH requester table groups.

`DEV1_EPF0_1` and `DEV2_EPF0_1` are larger complete endpoint-function blocks. In addition to the endpoint families above, each includes lane margining support: `MARGINING_PORT_CAP`, `MARGINING_PORT_CNTL`, `MARGINING_PORT_STATUS`, and per-lane `LANE_0` through `LANE_15_MARGINING_LANE_CNTL`/`STATUS`. These registers support PCIe link margining observation/control for each lane and are absent from the smaller EPF1/EPF7 patterns in this slice.

The `DEV2_EPF1_1` block begins at the standard PCI config header and continues through early AER logging: vendor/device IDs, command/status, revision/class-code fields, BARs, capability pointer, PM capability, PCIe device/link capability/control/status registers, MSI/MSI-X, vendor-specific enhanced capability, AER uncorrectable/correctable status and masks, AER capability/control, and `PCIE_HDR_LOG0`/`PCIE_HDR_LOG1`. The block is partial because later AER logs, TLP prefix logs, BAR enhanced capability, power, DPA, ACS/PASID/ARI, and TPH registers continue in a following chunk.

Many register names intentionally share the same offset because they represent adjacent fields in the same PCI configuration dword. Examples include `VENDOR_ID`/`DEVICE_ID`, `COMMAND`/`STATUS`, class-code bytes, `DEVICE_CNTL`/`DEVICE_STATUS`, `LINK_CNTL`/`LINK_STATUS`, MSI address/data aliases, DPA status/control, and ACS/PASID/ARI capability/control pairs. Consumers must use the shift/mask header or PCI config-field helpers to isolate the intended bits.

## APIs, Types, And Functions

There are no callable APIs or C types in this chunk. The public surface is the generated preprocessor namespace:

- `regBIF_CFG_DEVx_EPFy_1_REGISTER` gives the encoded register offset.
- `regBIF_CFG_DEVx_EPFy_1_REGISTER_BASE_IDX` gives the base-index selector, always `5` in this range.

AMDGPU code combines these constants with helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `RREG32_PCIE_PORT`, `WREG32_PCIE_PORT`, and field helpers driven by `nbio_7_2_0_sh_mask.h`. The direct NBIO 7.2 integration file, `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c`, includes both this offset header and the matching shift/mask header. DC resource files for DCN 3.0.1 and DCN 3.1 include this offset header for NBIO base/address integration.

## Control Flow

There is no local runtime control flow. Use of the macros follows the generated register-access pattern:

1. Driver code includes `nbio_7_2_0_offset.h` and selects a `reg...` macro for the target NBIO register.
2. It computes the MMIO or PCIe-port address using the base index and SOC15/NBIO access helpers.
3. It reads or writes a raw register value, normally using field positions from `nbio_7_2_0_sh_mask.h` to preserve unrelated bits.
4. Hardware interprets the resulting PCIe configuration, interrupt, error-reporting, link, BAR, power, DPA, isolation, or lane-margining state.

The implied hardware flows include PCI config enumeration, PCIe link training and equalization, MSI/MSI-X routing, AER status logging and masking, BAR sizing, DPA and power budgeting, ACS/PASID/ARI routing and isolation, TPH steering table configuration, and per-lane margining.

## State And Persistence Behavior

The header stores no software state and persists nothing. It names hardware-visible configuration and status registers. The persistence of those registers depends on NBIO reset domains, PCI bus reset, function-level reset, D3hot-to-D0 transitions, suspend/resume save-restore, firmware/BIOS initialization, and explicit AMDGPU or PCI core writes.

The represented state mixes read-only capability data, writable control bits, BAR and interrupt configuration, masks, latched status, diagnostic logs, and live link/lane status. The offset header cannot distinguish safe read-only fields from write-one-to-clear status or side-effectful controls. Code must rely on hardware documentation, PCIe semantics, and the matching shift/mask definitions before using read-modify-write sequences.

## Dependencies And Integration Points

This chunk depends on AMD's generated NBIO 7.2.0 register database. It must stay synchronized with `nbio_7_2_0_sh_mask.h`, which supplies field shifts and masks for these register names, and with any generated default/reset metadata available for this ASIC family.

The direct code integration points are AMDGPU NBIO and display resource code:

- `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` includes this header and the matching shift/mask header for NBIO 7.2 access.
- `drivers/gpu/drm/amd/display/dc/resource/dcn301/dcn301_resource.c` includes this header and composes NBIO base-relative register names for display resources.
- `drivers/gpu/drm/amd/display/dc/resource/dcn31/dcn31_resource.c` includes this header for similar DCN 3.1 NBIO address integration.

Semantic dependencies include the PCI and PCI Express specifications for endpoint configuration headers, PM capability, PCIe capability, MSI/MSI-X, AER, ACS, PASID, ARI, TPH requester tables, BAR enhanced capability, power budgeting, Dynamic Power Allocation, and lane margining. The macros are hardware-version-specific; similar names in other NBIO generations should not be substituted without verifying offsets and base indices.

## Risks And Edge Cases

- The range starts and ends inside endpoint-function blocks. Adjacent chunks are required for complete `DEV0_EPF6_1` and `DEV2_EPF1_1` analysis.
- Generated offset drift can compile cleanly while addressing the wrong PCIe config register, especially because the DEV/EPF families are highly repetitive.
- Shared dword offsets are expected, but they are easy to misuse without the matching field masks. Writing one named register can unintentionally change neighboring fields in the same dword.
- All `_BASE_IDX` values in this range are `5`; a wrong base selector would redirect otherwise correct offsets into the wrong NBIO aperture.
- MSI/MSI-X, AER, ACS, PASID, ARI, BAR sizing, DPA, TPH, and lane-margining controls can affect interrupt delivery, error containment, DMA isolation, link stability, power behavior, and performance.
- AER status/log and MSI pending/mask registers may have side effects or clear-on-write semantics. The offset macro alone is not enough to prove a read-modify-write is safe.
- Per-lane margining registers are repeated for lanes 0-15 and share control/status offsets per lane. Off-by-one or copy/paste mistakes can silently test or tune the wrong lane.
- These macros are untyped preprocessor constants, including large encoded offsets. Callers should keep established AMDGPU helper types and avoid ad hoc truncating casts.

## Test Signals

- Build AMDGPU NBIO 7.2 users, especially `amdgpu/nbio_v7_2.c` and DCN 3.0.1/3.1 resource files, to catch missing or renamed generated symbols.
- Run generated-header consistency checks: each `reg...` should have an adjacent `_BASE_IDX`, all base indices in this range should remain `5`, and repeated endpoint-function families should match expected per-device/per-function offset spacing.
- Cross-check register names against `nbio_7_2_0_sh_mask.h` so each offseted register has corresponding field definitions where fields are expected.
- On NBIO 7.2 hardware, compare decoded PCIe config-space state with `lspci -vvxxx`, PCI core dumps, or AMDGPU debug register reads for vendor/device IDs, BARs, PM state, link capabilities/status, MSI/MSI-X, AER, ACS/PASID/ARI, TPH, DPA, power-budget, and lane-margining registers.
- Exercise suspend/resume, PCIe retraining, FLR or GPU reset, MSI/MSI-X enable/disable, AER reporting, BAR sizing, and lane-margining paths to confirm callers use the intended offsets and preserve unrelated fields.

### subset-b-003159: lines 31261-31871

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_2_0_offset.h lines 31261-31871

## Purpose

This chunk is the final generated AMD NBIO 7.2.0 offset-map slice for device 2 endpoint functions in the BIF PCI configuration decode space. It starts in the middle of the `BIF_CFG_DEV2_EPF1_1` PCIe Advanced Error Reporting log area, completes the remaining `EPF1_1` enhanced-capability offsets, then defines the complete `BIF_CFG_DEV2_EPF2_1` endpoint configuration-space register offsets through the end of the header.

The file contains no executable driver logic. Its public surface is a set of C preprocessor constants that name hardware register offsets and their register-access base indices. AMDGPU and display code include this header so generated register names can be passed to the AMD register access macros for NBIO 7.2 hardware.

## Public Surface In This Chunk

The exported API is 603 `#define` constants in the generated offset-header pattern:

- `regBIF_CFG_DEV2_EPFx_1_<REGISTER>` gives the encoded MMIO/register address for a PCI/PCIe configuration register.
- `regBIF_CFG_DEV2_EPFx_1_<REGISTER>_BASE_IDX` gives the register access base index, which is consistently `5` throughout this chunk.

The `EPF1_1` portion continues from the previous chunk. It starts with `PCIE_HDR_LOG1_BASE_IDX`, then covers AER header log registers 2-3, TLP prefix logs 0-3, BAR enhanced capability registers for BAR1-BAR6, power budgeting, Dynamic Power Allocation, ACS, PASID, ARI, TPH requester capability/control, and TPH steering table entries 0-63.

The `EPF2_1` block starts at the generated marker `addressBlock: nbio_nbif0_bif_cfg_dev2_epf2_bifcfgdecp`. It defines standard endpoint PCI configuration header registers, PCI power-management capability registers, USB-related capability bytes such as `SBRN`, `FLADJ`, and `DBESL_DBESLD`, PCIe device/link capability and control registers, MSI/MSI-X registers, vendor-specific enhanced capability registers, AER registers and logs, BAR enhanced capability registers, power budgeting, DPA, ACS, PASID, ARI, TPH requester registers, and TPH steering table entries 0-63. The chunk then closes the header guard.

## Important Register Families

The `EPF1_1` tail is entirely PCIe enhanced-capability addressing. AER log offsets identify the captured header and TLP prefix fields associated with PCIe errors. BAR enhanced capability offsets describe the capability/control pairs for endpoint BAR1 through BAR6. Power budgeting registers expose the data selector, data, and capability slots used by software to inspect advertised power budget information.

The DPA group defines capability, latency indicator, status/control, and eight substate power allocation offsets. Several DPA names intentionally share offsets: `PCIE_DPA_STATUS` and `PCIE_DPA_CNTL` both resolve to `0x3fff80900497`, while substate allocation entries 0-3 share `0x3fff80900498` and entries 4-7 share `0x3fff80900499`; field-level access is supplied by the companion shift/mask headers. ACS, PASID, and ARI expose address translation/isolation and function-numbering capability/control registers. The TPH requester group includes the capability/control registers and 64 steering table logical entries, with pairs of table entries sharing each 32-bit register address.

The `EPF2_1` standard PCI header block maps endpoint identity, command/status, class code, cache/latency/header/BIST bytes, six BARs, CIS pointer, adapter ID, ROM BAR, capability pointer, interrupt line/pin, and latency grant fields. Its PM capability group includes capability list, capability, and status/control offsets. The PCIe capability group covers device and link capability/control/status registers, including PCIe 2.0 device/link capability and control/status offsets.

The `EPF2_1` interrupt groups define both MSI and MSI-X address/data/table/PBA locations, including 32-bit and 64-bit MSI data, mask, and pending locations. The AER group maps uncorrectable and correctable error status/mask/severity, capability/control, four header log registers, and four TLP prefix logs. The final enhanced-capability groups mirror the `EPF1_1` tail: BAR enhanced capability, power budgeting, DPA, ACS, PASID, ARI, TPH requester, and TPH steering table entries 0-63.

## Control Flow And State

There is no runtime control flow, branching, allocation, locking, or function dispatch in this header slice. The effective flow is compile-time substitution:

1. A translation unit includes `nbio_7_2_0_offset.h`.
2. The caller references a `regBIF_CFG_DEV2_EPF1_1_*` or `regBIF_CFG_DEV2_EPF2_1_*` macro.
3. AMDGPU register helper macros use the offset plus the `BASE_IDX` to reach the intended NBIO register aperture.
4. Field interpretation, masking, and composition are performed with companion shift/mask headers, not in this offset header.

This chunk stores no software state and has no persistence layer. The persistent and side-effectful state lives in the GPU's NBIO PCI/PCIe configuration registers. External callers decide when those registers are read, written, or cleared; this header only binds symbolic names to addresses.

## Dependencies And Integration Points

The mechanical dependency is the AMD generated register-header convention. This offset header must stay in sync with the companion NBIO 7.2.0 shift/mask and default headers, and with the ASIC register generator that produced the `reg...` and `_BASE_IDX` names. Shared offsets in the DPA and TPH groups depend on field masks from the corresponding `_sh_mask` file to distinguish logical fields within the same 32-bit register.

Direct inclusion points in this source tree include `drivers/gpu/drm/amd/amdgpu/nbio_v7_2.c` and display resource files under `drivers/gpu/drm/amd/display/dc/resource/dcn301/` and `dcn31/`. Those consumers do not get behavior from the header by itself; they use it as a register-address namespace for NBIO setup, feature discovery, link/power handling, and display resource code that needs NBIO 7.2 register definitions.

The semantic dependencies are the PCI and PCI Express configuration-space specifications: standard endpoint headers, PM capability, PCIe capability, MSI, MSI-X, vendor-specific enhanced capabilities, AER, enhanced BAR capability, power budgeting, DPA, ACS, PASID, ARI, and TPH requester/steering-table layout. The generated names encode those specifications but do not enforce valid programming sequences.

## Risks And Maintenance Notes

- The chunk begins mid-register-family: `EPF1_1_PCIE_HDR_LOG1_BASE_IDX` appears without its paired offset macro in this slice because the offset is in the previous chunk. The merged per-file report must reconcile adjacent chunks for a complete `EPF1_1` view.
- Every `_BASE_IDX` in this chunk is `5`; if the ASIC register generator or access macros expect a different base for a future NBIO variant, stale constants would route reads or writes to the wrong aperture.
- Repeated logical entries share physical offsets in DPA substate allocations and TPH steering tables. Callers must use the correct shift/mask definitions and avoid treating each logical name as an independent 32-bit register.
- AER status/log registers, MSI/MSI-X state, ACS/PASID/ARI controls, DPA controls, and TPH controls can affect interrupt delivery, isolation, error reporting, endpoint power behavior, and PCIe transaction handling. The presence of an offset macro does not imply that blind read-modify-write is safe.
- The `EPF2_1` block is highly repetitive relative to neighboring endpoint-function blocks and NBIO generations. Review drift is easy to miss because many names differ only by function prefix or table index.
- This header ends immediately after `EPF2_1_PCIE_TPH_ST_TABLE_63`; there are no trailing generated blocks after the header guard close. Any expected later capability for this endpoint must be verified against the hardware spec or regenerated headers.

## Test Signals

Useful validation signals for this chunk are:

- Build coverage for translation units that include `nbio_7_2_0_offset.h`, especially `amdgpu/nbio_v7_2.c` and the DCN 3.01/3.1 display resource files.
- Static generation checks that every non-partial register offset in the chunk has a matching `_BASE_IDX`, and that all base indices remain `5`.
- Cross-header checks that `EPF1_1` and `EPF2_1` register names here have corresponding field definitions in the NBIO 7.2.0 shift/mask header where the registers are not full-width raw values.
- Hardware or register-dump validation on NBIO 7.2 systems comparing decoded `EPF2_1` vendor/device/class fields, BARs, PM/PCIe capabilities, MSI/MSI-X tables, AER status/logs, ACS/PASID/ARI state, DPA state, and TPH steering table locations against PCI config dumps such as `lspci -vvxxx` and AMDGPU debug register reads.
- Error-path testing that observes or injects AER conditions and confirms that the header log and TLP prefix log offsets identify the intended captured error data.
- Power and transaction-path tests around power budgeting, DPA substate allocation, PASID/ARI exposure, ACS isolation settings, and TPH steering behavior, with special attention to registers where multiple logical names share one physical offset.
