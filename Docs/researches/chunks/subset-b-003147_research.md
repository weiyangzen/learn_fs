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
