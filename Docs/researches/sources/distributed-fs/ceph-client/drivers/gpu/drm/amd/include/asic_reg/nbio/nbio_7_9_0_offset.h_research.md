# Research: sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h

This per-file research report is synthesized from ordered chunk research reports.

## Chunk Map

- `subset-b-003323`: lines 1-2713, `Docs/researches/chunks/subset-b-003323_research.md`
- `subset-b-003324`: lines 2714-6013, `Docs/researches/chunks/subset-b-003324_research.md`
- `subset-b-003325`: lines 6014-9163, `Docs/researches/chunks/subset-b-003325_research.md`
- `subset-b-003326`: lines 9164-10004, `Docs/researches/chunks/subset-b-003326_research.md`

## Chunk Research

### subset-b-003323: lines 1-2713

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h lines 1-2713

## Scope

This chunk covers the first 2,713 lines of `nbio_7_9_0_offset.h`, an AMDGPU generated register-offset header for NBIO 7.9.0. The range starts with the include guard and covers the early NBIO/NBIF BIF, RCC, GDC, endpoint-function, root-complex, and PCI configuration-space offset definitions. The file has no functions or runtime control flow; it publishes numeric constants consumed by SOC15 register-access macros in the NBIO 7.9 driver and related RAS code.

## Purpose

The header maps hardware register names to dword or byte offsets and, for MMIO-style registers, maps each register to a `*_BASE_IDX` address-space selector. Driver code combines these constants with helpers such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_SOC15_OFFSET()`, and `WREG32_FIELD15_PREREG()` to calculate physical MMIO addresses for NBIO register reads and writes.

Within this chunk the constants mainly describe:

- NBIF/BIF indirect PCIe index and data registers, scratch registers, interrupt controls, MMIO remap/CAM registers, and firmware/BIOS/driver scratch storage.
- RCC downstream, downstream-port, endpoint, root-complex, strap, and endpoint-function registers for PCIe link, error, bus, requester ID, aperture, LTR, and power-management behavior.
- BIF physical-function registers for HDP flush request/done, doorbell self-ring aperture programming, mailbox buffers, transaction-pending state, and GPU partition capability/status.
- GDC bridge/control registers for A2S/S2A traffic, clock/power gating, SHUB interface, ATDMA, and doorbell status.
- PCI configuration-space views for device 0 endpoint functions 0 and 1, plus the root-complex view, including standard PCI header fields and extended PCIe capabilities such as AER, VC, BAR, power budget, DPA, ACS, ATS, PRI/page request, PASID, multicast, LTR, ARI, SR-IOV, data-link features, 16GT PHY, margining, resize-BAR, 32GT link, and AMD GPU IOV vendor-specific scheduler tables.

## Important APIs, Types, and Macros

This header defines preprocessor constants only. There are no C functions, structs, enums, or local state.

The important macro patterns are:

- `reg...`: register offsets used with SOC15/NBIO MMIO access helpers. Examples in this chunk include `regBIF_BX0_PCIE_INDEX2`, `regBIF_BX0_PCIE_DATA2`, `regBIF_BX0_PCIE_INDEX2_HI`, `regBIF_BX_PF0_GPU_HDP_FLUSH_REQ`, `regBIF_BX_PF0_GPU_HDP_FLUSH_DONE`, `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_BASE_LOW`, `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_BASE_HIGH`, `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_CNTL`, `regRCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`, and `regRCC_STRAP0_RCC_DEV0_EPF0_STRAP0`.
- `cfg...`: byte offsets in PCI configuration space. Endpoint function blocks use `cfgBIF_CFG_DEV0_EPF0_*` and `cfgBIF_CFG_DEV0_EPF1_*`; these name PCI header and enhanced capability fields as byte offsets.
- `*_BASE_IDX`: SOC15 register-base selector paired with a `reg...` macro. In this chunk the common base indices are `0` for some system/indirect indices, `1` for scratch/remap/system BIF fields, `2` for BIF/RCC register decoder fields, `3` for GDC, `4` for the GFX MSI-X table/PBA region, and `8` for PCI configuration-space register views.

Notable address blocks covered by the chunk:

- `aid_nbio_nbif0_bif_bx_SYSDEC`, lines 28-217: BIF PCIe index/data registers, BIOS/SBIOS/driver/FW scratch arrays, GFX MMIOREG CAM/remap registers, interrupt controls, MMIO remap targets, and indirect access controls.
- `aid_nbio_nbif0_rcc_dwn_dev0_BIFDEC1`, `aid_nbio_nbif0_rcc_dwnp_dev0_BIFDEC1`, and `aid_nbio_nbif0_rcc_ep_dev0_BIFDEC1`, lines 218-333: RCC downstream, downstream-port, and endpoint PCIe control/status/register-strap definitions.
- `aid_nbio_nbif0_bif_bx_pf_SYSPFVFDEC`, lines 334-349: PF0 MM and RSMU indirect index/data registers.
- `aid_nbio_nbif0_bif_bx_BIFDEC1`, lines 350-471: BIF reset, interrupt, FB enable, BACO, LUT, reset-status, and flush/remap controls.
- `aid_nbio_nbif0_rcc_dev0_BIFDEC1`, lines 472-559: device 0 RCC scratch, interrupt, error, ATOMIC, config aperture, bus-number, peer FB offset, link, requester ID restore, LTR, and arbitration registers.
- `aid_nbio_nbif0_rcc_dev0_epf0_BIFDEC2`, lines 560-597: four GFX MSI-X vectors and PBA dword offsets.
- `aid_nbio_nbif0_rcc_strap_BIFDEC1`, lines 598-701: RCC/BIF/device/function strap register offsets.
- `aid_nbio_nbif0_bif_bx_pf_BIFPFVFDEC1`, lines 702-761: PF0 status, HDP flush, doorbell aperture, mailbox, and partition registers.
- `aid_nbio_nbif0_rcc_dev0_epf0_BIFPFVFDEC1[13440..14975]`, lines 762-775: EPF0 RCC error, doorbell aperture enable, memory-size, reserved, and IOV function identifier registers.
- `aid_nbio_nbif0_gdc_GDCDEC`, lines 776-819: GDC A2S/S2A, SHUB, MGCG, doorbell, ATDMA, and power-gating control registers.
- `aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`, lines 820-1317 and 1817-2713: endpoint function 0 PCI config-space offsets, first as `cfg...` byte offsets and later as `reg...` dword offsets under base index 8.
- `aid_nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp`, lines 1318-1440: endpoint function 1 PCI config-space offsets.
- `aid_nbio_nbif0_bif_cfg_dev0_rc_bifcfgdecp`, lines 1441-1816: root-complex PCI config-space offsets under base index 8.

## Control Flow

There is no executable control flow in this chunk. Runtime control flow is supplied by the AMDGPU driver code that includes this header:

- `amdgpu/nbio_v7_9.c` includes this header and uses offsets from this chunk to configure NBIO. Examples include reading `regRCC_STRAP0_RCC_DEV0_EPF0_STRAP0` for revision ID on PF/bare-metal paths, reading `regRCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`, enabling FB access via `regBIF_BX0_BIF_FB_EN`, programming doorbell self-ring aperture base/control through `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_*`, configuring interrupt control through `regBIF_BX0_INTERRUPT_CNTL*`, returning HDP flush offsets from `regBIF_BX_PF0_GPU_HDP_FLUSH_REQ/DONE`, and returning indirect PCIe register offsets from `regBIF_BX0_PCIE_INDEX2`, `regBIF_BX0_PCIE_DATA2`, and `regBIF_BX0_PCIE_INDEX2_HI`.
- `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` includes the same offset and mask headers. Its current NBIO 7.9 RAS controller and ATHUB error interrupt hooks are mostly registration/dummy handlers, but the include ties the RAS source to this ASIC register namespace and IRQ source definitions.

## State and Persistence Behavior

The header itself persists no software state. Its constants point to hardware state that is persistent at device scope until reset, power transition, firmware action, or explicit driver reprogramming.

State-sensitive groups in this chunk include:

- Scratch registers: SBIOS, BIOS, driver, firmware, and BIF/RCC scratch registers can retain handoff or diagnostic data across driver phases depending on reset domain.
- Doorbell aperture registers: `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_BASE_*`, `regBIF_BX_PF0_DOORBELL_SELFRING_GPA_APER_CNTL`, and `regRCC_DEV0_EPF0_RCC_DOORBELL_APER_EN` control CPU/GPU doorbell routing and are active hardware configuration.
- HDP flush registers: `regBIF_BX_PF0_GPU_HDP_FLUSH_REQ` and `regBIF_BX_PF0_GPU_HDP_FLUSH_DONE` participate in cache/coherency synchronization between engines and host-visible memory.
- Partition registers: `regBIF_BX_PF0_PARTITION_COMPUTE_CAP`, `regBIF_BX_PF0_PARTITION_MEM_CAP`, `regBIF_BX_PF0_PARTITION_COMPUTE_STATUS`, and `regBIF_BX_PF0_PARTITION_MEM_STATUS` expose current and supported compute/memory partition modes.
- PCI config capability fields: SR-IOV, ATS, PRI, PASID, ACS, BAR, resize-BAR, DPA, AER, link-training, margining, and GPUIOV scheduler-table offsets describe device-visible configuration state used by host PCI enumeration, virtualization, and error handling.

## Dependencies

This header depends only on the C preprocessor and the AMDGPU SOC15 register-access convention. It is intended to be paired with:

- `nbio/nbio_7_9_0_sh_mask.h` for bit masks and shifts used with these offsets.
- SOC15 register macros and accessors from the AMDGPU core, including `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_SOC15_EXT`, and `WREG32_FIELD15_PREREG`.
- The NBIO 7.9 implementation in `amdgpu/nbio_v7_9.c`, which maps the constants into driver-visible callbacks.
- RAS and IRQ-source code using NBIO client/source IDs, including `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` and `ivsrcid/nbio/irqsrcs_nbif_7_4.h`.

## Integration Points

The most direct integration point is `nbio_v7_9.c`, whose `nbio_v7_9_funcs` and related exported structures provide the NBIO services used by the wider AMDGPU driver. Offsets from this chunk feed these services:

- HDP flush offset discovery for GPU engine cache-flush synchronization.
- PCIe indirect index/data register selection for PCIe register access.
- Memory-controller aperture enable/disable through BIF FB enable.
- Doorbell aperture and self-ring programming for queues and interrupt handling.
- Interrupt control setup for IH behavior and dummy page address programming.
- Compute and memory partition mode queries.
- ASIC revision and memory-size reads.

The PCI configuration-space definitions also integrate with the broader PCIe and virtualization model. The chunk exposes config offsets for PF/EPF0, EPF1, root complex, and SR-IOV/GPUIOV capability structures. Even when a specific macro is not referenced by the current C sources, it is part of the generated ASIC register contract and may be consumed by diagnostics, bring-up code, RAS extensions, virtualization paths, or future driver code.

## Risks and Edge Cases

- Offset/base-index mismatches are high impact. A wrong `*_BASE_IDX` or offset can redirect a read/write to a different hardware aperture, causing silent misconfiguration, failed PCIe access, invalid doorbell routing, coherency failures, or hangs.
- Several symbolic fields intentionally alias the same offset because multiple PCI fields share a dword. Examples include MSI fields, DPA substate allocations, lane equalization pairs, status/control pairs, and capability headers. Consumers must use the corresponding shift/mask header rather than treating each name as a unique register.
- `cfg...` byte offsets and `reg...` dword offsets are both present for related PCI config blocks. Mixing the two addressing units would produce incorrect accesses.
- The chunk ends mid-address-block at `regBIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_GFX3SCH_DW6`; later GFX scheduler dwords and following blocks are outside this chunk and must be reconciled with later research chunks.
- Virtualization-related registers such as SR-IOV, ATS, PRI/page request, PASID, GPUIOV scheduler tables, and mailbox registers are sensitive to PF/VF privilege and hypervisor expectations. Incorrect programming can expose or break guest-visible device state.
- Some RAS interrupt paths for NBIO 7.9 are currently dummy handlers due to a noted BIF ring hardware issue in the RAS source. That means interrupt registration may compile and initialize while runtime processing is intentionally inert.

## Test Signals

Useful validation signals for changes touching this header or consumers include:

- Build coverage of `amdgpu/nbio_v7_9.c` and `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` with `nbio_7_9_0_offset.h` and `nbio_7_9_0_sh_mask.h` included together; compile failures often catch renamed or missing register macros.
- Boot/probe logs showing successful NBIO initialization on NBIO 7.9 hardware, including revision ID and memory-size reads.
- Successful GPU queue submission and interrupt handling, which exercise doorbell aperture, IH interrupt-control, and HDP flush offset callbacks.
- PCIe indirect register access tests through the `PCIE_INDEX2`, `PCIE_DATA2`, and `PCIE_INDEX2_HI` offsets.
- Coherency tests that stress CP and SDMA HDP flush request/done paths.
- SR-IOV or partition-mode validation on supported hardware, checking that PCI config-space capabilities, mailbox paths, and compute/memory partition status reads remain consistent.
- RAS IRQ registration checks for BIF client/source IDs, while accounting for the current dummy processing behavior in NBIO 7.9 RAS controller and ATHUB error-event handlers.

### subset-b-003324: lines 2714-6013

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h lines 2714-6013

## Chunk Scope

- Work item: `subset-b-003324`
- Source chunk: `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h`, lines 2714-6013
- Parent file role: generated AMDGPU NBIO 7.9.0 register offset map used with SOC15/NBIO register access helpers.
- Chunk shape: 3,252 preprocessor definitions, representing 1,626 register symbols plus one paired `*_BASE_IDX` definition for each symbol. Every visible `*_BASE_IDX` in this span is `8`.

## Purpose

This chunk provides symbolic register offsets for NBIO 7.9.0 BIF/NBIF PCI configuration, RCC control, MSI-X table/PBA, strap, reset, doorbell, and PF/VF base-address register spaces. It has no executable logic. AMDGPU code combines these generated `reg*` names with the matching `_BASE_IDX` metadata through helpers such as `SOC15_REG_OFFSET`, `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, and `WREG32_FIELD15_PREREG`.

The range begins in the tail of the previous `aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block, where EPF0 vendor-specific GPUIOV scheduler dwords and interrupt-enable/status registers are still being listed. It then covers a complete direct-MMIO config-space view for `DEV0_EPF1`, RCC link/endpoint/downstream controls, a 256-entry MSI-X vector table and 8-dword pending-bit array, SUM indirect index/data registers, a large RCC strap region, BIF reset/interrupt/D-state registers, and the beginning of the BIF miscellaneous region through PF/VF AID base-address maps.

This is register ABI documentation, not Ceph or distributed-filesystem logic. The `ceph-client` path is the repository mirror location; the content is AMD GPU kernel hardware interface data.

## Major Register Families In This Chunk

- Lines 2714-2806 finish the visible tail of `aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp`. The visible symbols include `BIF_CFG_DEV0_EPF0_0_PCIE_VENDOR_SPECIFIC_HDR_GPUIOV_GFX2SCH_DW0` through `GFX7SCH_DW8`, followed by GPUIOV `ENGA`/`ENGB` interrupt enable and status registers for engine ranges `A0_7`, `A8_15`, `B0_7`, and `B8_15`.
- Lines 2808-3048 define `aid_nbio_nbif0_bif_cfg_dev0_epf1_bifcfgdecp` at base address `0x10141000`. This is a direct register-index view of PCI function `DEV0_EPF1`, starting at register index `0x10400`. It includes standard PCI header aliases, BARs, ROM BAR, capability pointer, interrupt fields, PM capability, PCIe device/link capabilities, MSI/MSI-X capability registers, vendor-specific enhanced capability dwords, AER status/mask/severity/logging, TLP prefix logs, enhanced BAR capability/control registers, power-budget registers, DPA, ACS, PASID, and ARI.
- Lines 3050-3072 define `aid_nbio_nbif0_rcc_dev0_RCCPORTDEC` at base `0x10131000`. These `RCC_DEV0_1_*` registers expose VDM support, bus control, feature/misc control, device/common link controls, requester-ID restore, LTR switch control, memory-hub arbitration, and link margining parameter controls.
- Lines 3074-3132 define `aid_nbio_nbif0_rcc_ep_dev0_RCCPORTDEC`, the endpoint side of RCC/PCIe control. It includes scratch/control/status, interrupt control/status, RX/TX/bus/config controls, TX LTR control, strap misc registers, function-0 DPA capability/control/substate allocation aliases, PME control, TX requester ID, error control, and link speed control.
- Lines 3134-3156 define `aid_nbio_nbif0_rcc_dwn_dev0_RCCPORTDEC`, the downstream-side RCC/PCIe controls: reserved/scratch/control/config/RX/bus/cfg registers plus downstream strap fields for function 0.
- Lines 3158-3172 define `aid_nbio_nbif0_rcc_dwnp_dev0_RCCPORTDEC`, downstream-port error, RX, link-speed/link-control, strap, and LTR message information registers.
- Lines 3174-3194 define `aid_nbio_nbif0_rcc_pfc_amdgfx_RCCPFCDEC`, with PFC LTR, PME restore, sticky restore dwords 0-5, and auxiliary power control.
- Lines 3196-5246 define `aid_nbio_nbif0_pciemsix_0_usb_MSIXTDEC` at base `0x10168000`. This is the MSI-X table window, with vector entries `0` through `255`; each vector has `ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL` dwords at a regular four-register stride from `0x1a000` through `0x1a3ff`.
- Lines 5248-5266 define `aid_nbio_nbif0_pciemsix_0_usb_MSIXPDEC` at base `0x10169000`, the MSI-X pending-bit array registers `PCIEMSIX_PBA_0` through `PCIEMSIX_PBA_7`.
- Lines 5268-5276 define `aid_nbio_nbif0_bif_swus_SUMDEC`, containing `SUM_INDEX`, `SUM_DATA`, and `SUM_INDEX_HI` for an indexed sideband/summary register access path.
- Lines 5278-5648 define `aid_nbio_nbif0_rcc_strap_rcc_strap_internal`. This region lists strap registers for RCC device ports, BIF straps, `DEV0_EPF0` and `DEV0_EPF1`, `DEV0_EPF2` through `DEV0_EPF7`, `DEV1_EPF0/1`, and `DEV2_EPF0/1/2`. Several strap sequences intentionally skip numbers where the generated register database has no visible macro in this span.
- Lines 5650-5702 define `aid_nbio_nbif0_bif_rst_bif_rst_regblk`. Important symbols include hard and self soft reset controls, VPU reset, reset miscellaneous controls, PF0/PF1 FLR and D3hot-to-D0 reset controls, instance/PF FLR/D3hot/power/PF D-state interrupt status and mask registers, PF FLR reset, and D-state value registers.
- Lines 5704-6013 begin `aid_nbio_nbif0_bif_misc_bif_misc_regblk`. The visible portion contains ROM offset and BIOS strap controls, `DOORBELL0_CTRL_ENTRY_0` through `DOORBELL0_CTRL_ENTRY_20`, and base-address mapping registers for `VF0` through `VF7` plus `PF` across AID, XCC, NBIF, ATHUB, IH, and HDP destinations. The chunk ends after `regAID0_XCC1_PF_BASE_ADDR`.

## Important APIs, Types, And Symbols

There are no C functions, structs, enums, or storage objects in this chunk. The public API is entirely preprocessor constants:

- Register-offset macros such as `regBIF_CFG_DEV0_EPF1_0_COMMAND`, `regRCC_EP_DEV0_1_EP_PCIE_INT_STATUS`, `regPCIEMSIX_VECT255_CONTROL`, `regPCIEMSIX_PBA_7`, `regSUM_INDEX_HI`, `regRCC_STRAP1_RCC_DEV0_EPF1_STRAP25`, `regDEV0_PF0_FLR_RST_CTRL`, `regDOORBELL0_CTRL_ENTRY_20`, and `regAID0_NBIF_VF7_BASE_ADDR`.
- Paired base-index macros such as `regBIF_CFG_DEV0_EPF1_0_COMMAND_BASE_IDX`, `regPCIEMSIX_VECT0_ADDR_LO_BASE_IDX`, and `regBIF_PF_FLR_INTR_MASK_BASE_IDX`, all set to `8`. The base index selects the generated NBIO register-base segment; the numeric offset alone is not enough to compute an MMIO address.
- PCI configuration aliases in `BIF_CFG_DEV0_EPF1_0_*`. Multiple logical fields can share one dword index: vendor/device IDs at `0x10400`, command/status at `0x10401`, class-code bytes at `0x10402`, cache/latency/header/BIST at `0x10403`, MSI address/data/mask/pending aliases, DPA status/control aliases, DPA substate allocations packed four per dword, ACS capability/control aliases, PASID capability/control aliases, and ARI capability/control aliases.
- MSI-X table symbols with a strict vector layout: `regPCIEMSIX_VECTN_ADDR_LO`, `ADDR_HI`, `MSG_DATA`, and `CONTROL`. This layout is normally consumed by PCI/MSI-X programming and interrupt validation code rather than by bespoke per-vector logic.
- Strap and reset symbols that are stateful hardware configuration points. AMDGPU NBIO 7.9 code reads the EPF0 strap revision ID via `regRCC_STRAP0_RCC_DEV0_EPF0_STRAP0` from an earlier chunk of this same header, and this chunk continues many adjacent strap names used by the same register family.
- Doorbell and base-address mapping symbols in the visible `bif_misc` portion. `nbio_v7_9.c` uses `regDOORBELL0_CTRL_ENTRY_*` macros for SDMA/VCN doorbell routing, and the AID/XCC/NBIF/ATHUB/IH/HDP base-address symbols describe per-PF/VF routing apertures.

## Control Flow

This header has no executable control flow. Runtime flow is created by AMDGPU users of the symbols:

1. Driver code selects a generated NBIO 7.9.0 register macro matching the active hardware path.
2. SOC15/NBIO access helpers combine the macro value, its `*_BASE_IDX`, the NBIO IP block, and an instance/AID offset into an MMIO address.
3. The driver reads, writes, polls, or field-updates that address, often using the matching `nbio_7_9_0_sh_mask.h` definitions with `REG_GET_FIELD`, `REG_SET_FIELD`, or `WREG32_FIELD15_PREREG`.

The control-flow significance of this chunk is data-driven. PCI config setup depends on the `BIF_CFG_DEV0_EPF1_0_*` layout; interrupt setup depends on MSI/MSI-X table/PBA and doorbell offsets; reset and power-state handling depends on BIF reset/D-state offsets; and PCIe link, LTR, DPA, PME, and error paths depend on RCC endpoint/downstream offsets.

## State And Persistence Behavior

The file itself owns no mutable state, allocates no memory, performs no I/O, and persists nothing. The registers it names represent hardware state:

- PCI function identity and configuration state for `DEV0_EPF1`: command/status, class codes, BARs, ROM, PM capability, PCIe capability, MSI/MSI-X, AER, enhanced BAR, power-budget, DPA, ACS, PASID, and ARI fields.
- GPUIOV vendor-specific scheduler and interrupt state in the EPF0 tail: visible GFX scheduler dwords and ENGA/ENGB interrupt enable/status registers.
- PCIe/RCC link and endpoint state: VDM, requester ID restore, LTR, arbitration, DPA, PME, error controls, link speed controls, downstream config controls, and PFC restore/sticky/aux power settings.
- MSI-X state: 256 vector address/data/control entries and 8 pending-bit-array dwords. Vector control fields may mask delivery, while PBA bits reflect pending interrupts.
- Strap state: configuration straps for ports, BIF, endpoint functions, and devices. These are generally sampled/configuration-like hardware state and may be reset- or firmware-dependent.
- Reset and power transition state: hard/self resets, FLR, D3hot-to-D0 reset controls, interrupt status/mask registers, and D-state value registers.
- Doorbell and routing aperture state: `DOORBELL0_CTRL_ENTRY_*` ranges and per-PF/VF AID/XCC/NBIF/ATHUB/IH/HDP base-address maps that route queue notifications or function apertures.

Persistence across GPU reset, FLR, D3 transitions, BACO, suspend/resume, or firmware handoff is not described by this header. Those semantics belong to the hardware and driver sequences. A stale generated offset can still create persistent driver behavior because compiled code will keep targeting the wrong register until the header is regenerated and rebuilt.

## Dependencies And Integration Points

- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` includes this header and `nbio_7_9_0_sh_mask.h`. It uses NBIO 7.9 register offsets for revision ID, framebuffer access, memory size, HDP remap, doorbell ranges, doorbell aperture enabling, and other NBIO setup paths.
- `sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c` includes the same offset/mask pair for NBIO RAS interrupt integration, although the visible functions in that file mostly register dummy interrupt handlers because the relevant BIFring path is disabled by hardware behavior.
- The matching `nbio_7_9_0_sh_mask.h` supplies bit positions and masks. Offset macros in this chunk identify dword/register locations; safe field manipulation requires the sibling mask/shift header.
- The AMDGPU SOC15 register-base infrastructure supplies the meaning of base index `8`. These constants should not be used as flat physical addresses.
- Adjacent generated NBIO headers such as `nbio_7_2_0_offset.h`, `nbio_7_7_0_offset.h`, and `nbio_7_11_0_offset.h` define similar families with generation-specific offsets and base indices. Porting code across ASIC generations must use the header selected by the owning NBIO implementation.

## Risks And Edge Cases

- The chunk starts inside an already-open EPF0 config block and ends inside the BIF miscellaneous block. Merge/reconciliation must preserve the previous block context for the GPUIOV tail and the next block continuation for remaining PF/VF base-address or misc registers.
- All visible base indices are `8`; using these numeric offsets with a helper expecting another base index can silently address the wrong register window.
- PCI config aliases intentionally share dword offsets. Treating every macro name as a unique physical register would be wrong for command/status, capability/control/status pairs, MSI aliases, packed DPA allocations, ACS/PASID/ARI cap/control pairs, and interrupt-line/pin/grant/latency fields.
- The MSI-X table is large and mechanically regular. Off-by-one vector indexing or stride mistakes can program one vector's address/data/control while the driver believes it has programmed another vector.
- MSI-X vector table and PBA registers are interrupt-critical. Wrong offsets can cause missed interrupts, stale pending bits, vectors delivered to the wrong CPU address/data pair, or stuck masked vectors.
- RCC link, DPA, PME, LTR, requester-ID, and link-speed controls are PCIe behavior controls. Incorrect writes can cause link training failures, broken low-power transitions, ordering/latency regressions, or enumeration problems.
- Strap registers are configuration-sensitive and often reset-sampled. Debug or bring-up code should avoid broad write sweeps across strap ranges unless the hardware programming model explicitly allows it.
- Reset and D-state registers are high blast-radius controls. Misaddressed FLR, D3hot-to-D0, hard reset, or interrupt-mask writes can hang a function, lose device state, or hide recovery events.
- Doorbell and AID/PF/VF base-address registers affect queue notification and virtualization routing. Wrong values can break SDMA/VCN queue wakeups, PF/VF isolation, or per-AID routing.
- Similar symbol families repeat across EPF numbers, device numbers, VF numbers, AID numbers, and XCC instances. Manual edits or cross-generation copy/paste are especially likely to compile cleanly but route to the wrong hardware function.

## Test And Validation Signals

- Build coverage: compile AMDGPU paths that include `nbio_7_9_0_offset.h` and `nbio_7_9_0_sh_mask.h`, especially `amdgpu/nbio_v7_9.c` and `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, to catch missing or renamed generated symbols.
- Generated-header consistency: verify each visible `reg*` macro has exactly one matching `reg*_BASE_IDX` macro, and that every visible base index remains the expected value `8`.
- PCI config validation: on matching NBIO 7.9 hardware, decode `DEV0_EPF1` config-space reads using these offsets and the sibling masks; verify identity, BARs, capability chain, PM/PCIe/MSI/MSI-X/AER/enhanced capability offsets, ACS/PASID/ARI presence, and intentional aliasing.
- MSI-X validation: program representative low, middle, and high vectors, including vector 0 and vector 255, then confirm address/data/control and PBA behavior match the four-dword stride and 8-dword PBA layout.
- Doorbell validation: exercise SDMA and VCN queues through `nbio_v7_9.c` doorbell programming paths, including multi-AID offsets, and confirm interrupts/work submissions arrive without spurious routing.
- Reset and power validation: exercise FLR, D3hot-to-D0, suspend/resume, and recovery paths while checking BIF reset interrupt status/mask and D-state value registers.
- PCIe/RCC validation: cover link speed changes, LTR behavior, PME/DPA paths, requester-ID restore, and AER/error-control behavior under normal operation and controlled PCIe error tests.
- Strap and revision validation: compare strap-derived values and function strap layouts against hardware documentation or known-good register dumps for NBIO 7.9 devices.
- Static cross-version checks: compare repeated EPF, RCC, MSI-X, strap, doorbell, and AID/PF/VF base-address families against adjacent NBIO generated headers to catch accidental use of NBIO 7.2/7.7/7.11 offsets in NBIO 7.9 code.

## Notes For Merge/Reconciliation

- This is a chunk-level report only for `subset-b-003324`; no final per-file report was produced.
- The chunk starts at line 2714 inside the previous `aid_nbio_nbif0_bif_cfg_dev0_epf0_bifcfgdecp` address block, whose marker appears earlier in the file. The visible EPF0 content here is only the GPUIOV/vendor-specific tail.
- The chunk includes a complete `DEV0_EPF1` direct config-space block and complete visible RCC/MSI-X/PBA/SUM/strap/reset blocks, then ends in the middle of the BIF miscellaneous register block after `regAID0_XCC1_PF_BASE_ADDR`.
- Keep this report under `Docs/researches/chunks/`; the merge lane should synthesize the source-file report after all chunks for `nbio_7_9_0_offset.h` are available.

### subset-b-003325: lines 6014-9163

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h lines 6014-9163

## Purpose

This chunk is a generated register-offset map for AMD NBIO 7.9.0 hardware. It does not implement executable logic; it gives the AMDGPU driver compile-time names for MMIO, indexed, and PCI configuration-space offsets used by the SOC15 register access helpers. The line range covers the end of one NBIF/BIF register group, several `aid_nbio_nbif0_*` address blocks, IOHUB northbridge/IOMMU/RAS blocks, root-complex PCIe config space, SR-IOV VF config-space mirrors for VF0-VF7, and the beginning of VF0 PF/VF decode aliases.

Within this chunk there are 2,954 `#define`s: 1,894 address/value definitions and 1,060 matching `_BASE_IDX` definitions. The `reg*` symbols represent SOC15 MMIO/register-space offsets; the `cfg*` symbols represent PCI configuration-space offsets. Most registers in the `0x10120000`, `0x13b*`, `0x14300000`, and `0x15700000` address blocks have `_BASE_IDX 8`, GDC/SYSHUB registers under `0x1400000` use `_BASE_IDX 5`, and the VF-local PF/VF decode aliases at base `0x0` use `_BASE_IDX 2` or `0`.

## Important APIs, Types, and Macro Families

There are no C functions, structs, or enums in this chunk. The important API surface is the macro namespace consumed by AMDGPU register helpers:

- `regAID*_PF_BASE_ADDR` and `regAID*_XCC*_PF_BASE_ADDR`: AID/XCC PF base address aliases at offsets `0xcdc3` through `0xcdcb`.
- `regBIFC_DOORBELL_ACCESS_EN_PF` and `regBIFC_DOORBELL_ACCESS_EN_VF0` through `VF7`: PF/VF doorbell access enable registers used to gate doorbell pass-through behavior.
- `regBIFC_*`, `regNBIF_*`, `regSMN_MST_*`, and `regBIF_*`: BIF/NBIF control, interrupt, error logging, PASID, performance counter, power-gating, clock-gating, strap, timeout, and SDP/GMI credit-control registers.
- `regRCC_DWN_DEV0_2_*`, `regRCC_DWNP_DEV0_2_*`, `regRCC_EP_DEV0_*`, `regRCC_DEV0_*`, and `regRCC_STRAP2_*`: root-complex controller PCIe endpoint/downstream control, link/power/DPA state, requester ID, reset/config aperture, GPU IOV, peer register/FB offsets, bus-number capture, and strap registers.
- `regBIF_BX1_*` and `regBIF_BX_PF1_*`: BIF BX system/PF registers for indirect PCIe index/data windows, BIOS and driver scratch registers, MMIO register CAM remapping, VF enable/status controls, HDP flush remap controls, BIF ring pointers, mailbox registers, pad controls, and partition capability/status.
- `regS2A_DOORBELL_ENTRY_*_CTRL`, `regS2A_DOORBELL_COMMON_CTRL_REG`, `regGDC1_*`, `regXCC_DOORBELL_FENCE`, and `regSHUB_*`: GDC, S2A doorbell routing, XCC doorbell fence, reset, and host/SYSHUB integration registers. `amdgpu/nbio_v7_9.c` uses these S2A doorbell-entry offsets when programming SDMA, VCN, and IH doorbell routing.
- `regHST_CLK*`, `regDMA_CLK*`, and `regNIC400_*`: SYSHUB direct clock/control and NIC400 fabric QoS/outstanding transaction controls.
- `regNB_*`, `regSW_*`, `regCAM_*`, `regTRAP*`, and `regSB_*`: IOHUB northbridge config and misc registers for bus/MMIO/DRAM windows, southbridge location, NMI/SMI/SCI/GIC handling, CAM target data, PSP/SMU base addresses, SMU CPU blocking, trap request/response windows, and bridge config fields.
- `regPARITY_*`, `regRAS_*`, and `reg*ACTION_CONTROL`: IOHUB NB RAS configuration, parity severity/status/counter groups, global RAS status, RAS scratch, and action-control registers for PCIe port errors.
- `regNB_PCIE0DEVINDCFG*`, `regNB_NBIF1DEVINDCFG0_*`, `regNB_INTSBDEVINDCFG0_*`, `regNB_PCIE0RCBDG_INDCFG*`, and `regNB_NBIF1RCBDG_INDCFG0_*`: indirect SMN index/data windows for PCIe device and root-complex bridge configuration blocks.
- `regL2_*`, `regL2A_*`, `regL2B_*`, `regPPR_CONTROL`: IOMMU L2 A/B performance, control, page-size, translation/cache way, error-rule, power/clock-gating, update-filter, and PPR controls.
- `regFEATURES_ENABLE`: IOAPIC feature enable register.
- `cfgBIF_CFG_DEV0_RC_*`: root-complex PCI config offsets, including standard header fields, bridge windows, MSI, PCIe/VC/DSN/AER/secondary PCIe/link equalization, ACS, DLF, 16 GT/s, lane margining, and 32 GT/s capability fields.
- `cfgBIF_CFG_DEV0_EPF0_VF{0..7}_*`: repeated virtual-function PCI config offset maps for SR-IOV VF0 through VF7, covering standard config header, BARs, MSI/MSI-X, PCIe vendor-specific caps, AER logs, ATS, and ARI.
- `regBIF_BX_DEV0_EPF0_VF0_*`, `regBIF_BX_DEV0_EPF0_VF0_MM_*`, and `regRCC_DEV0_EPF0_VF0_RCC_*`: VF0 local PF/VF decode aliases for BME/atomic status, doorbell self-ring GPA aperture, HDP coherency flush/invalidate controls, GPU HDP flush request/done, transaction-pending status, mailbox buffers/control/interrupts, MM index/data windows, and VF0 RCC memory/doorbell config.

## Control Flow

The header has no branches or runtime control flow. Its control effect appears only after inclusion by C files that call AMDGPU register access macros such as `RREG32_SOC15`, `WREG32_SOC15`, `WREG32_SOC15_OFFSET`, `WREG32_SOC15_EXT`, `WREG32_FIELD15_PREREG`, and `SOC15_REG_OFFSET`.

For example, `amdgpu/nbio_v7_9.c` includes this header and uses chunk-defined offsets to:

- Enable PF doorbell pass-through via `regBIFC_DOORBELL_ACCESS_EN_PF`.
- Toggle the RCC doorbell aperture through `regRCC_DEV0_EPF0_RCC_DOORBELL_APER_EN`.
- Read memory sizing through `regRCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`.
- Program S2A doorbell routing with `regS2A_DOORBELL_ENTRY_*_CTRL` for SDMA, VCN, and IH clients.

Because the macros are constants, call-site control flow is driven by the consuming NBIO logic and the hardware state. A wrong offset or base index here changes which hardware register the existing control flow touches.

## State and Persistence Behavior

This chunk defines hardware state locations but stores no software state. Persistence is entirely in the target hardware registers:

- Doorbell aperture and S2A routing registers persist until reset or reprogramming and affect command submission, interrupt handling, and multimedia/SDMA doorbell delivery.
- RCC, BIF, and NBIF registers influence PCIe endpoint/root-complex behavior, request routing, bus numbering, reset handling, peer memory windows, and GPU IOV partitioning.
- BIOS/driver scratch registers can be used as firmware-driver coordination state.
- RAS/parity status and counter registers reflect hardware error state and may require explicit clearing by code outside this chunk.
- IOMMU L2 registers affect translation/cache/performance behavior and are stateful hardware controls.
- PCI config-space macros describe standard and extended capabilities exposed to the host or virtual functions; their values are hardware/firmware-backed, not stored by this header.

## Dependencies

The chunk depends on the AMD SOC15 register access convention:

- `_BASE_IDX` values must match the register's SOC15 aperture/base table entry used by `SOC15_REG_OFFSET` and the read/write helpers.
- Bitfield programming depends on the sibling mask/shift header `nbio_7_9_0_sh_mask.h`; offsets here identify the register, while the mask header identifies fields within it.
- Interrupt source IDs used with NBIO are supplied by `ivsrcid/nbio/irqsrcs_nbif_7_4.h`.
- Runtime consumers are in the AMDGPU NBIO and RAS code, especially `drivers/gpu/drm/amd/amdgpu/nbio_v7_9.c` and `drivers/gpu/drm/amd/ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`.
- The generated register map must stay aligned with the actual NBIO 7.9.0 ASIC register database and with equivalent generated headers for adjacent ASICs.

## Integration Points

The primary integration point is AMDGPU's `adev->nbio` operation table and NBIO initialization/control routines. These offsets let NBIO code program doorbells, memory-controller access windows, PCIe link/root-complex behavior, self-ring apertures, RAS interrupt wiring, and hardware virtualization surfaces without hard-coded numeric addresses in the driver body.

The config-space aliases integrate with PCIe enumeration and SR-IOV virtualization. The root-complex block maps bridge and extended capability offsets, while the repeated VF0-VF7 blocks describe the exposed virtual function config layout. The VF-local decode aliases at the end of the chunk are especially relevant to SR-IOV guests or host-mediated VF handling because they expose VF0 mailbox, HDP flush, transaction-pending, and RCC memory/doorbell controls through a different base index.

The IOHUB and IOMMU blocks connect NBIO to platform fabric functions outside classic graphics command submission: RAS accounting, interrupt routing, northbridge window setup, trap machinery, IOAPIC features, IOMMU L2 controls, and SMN indirect access windows.

## Risks and Edge Cases

- Offset drift is high impact. A stale generated offset can write the wrong NBIO/RCC/IOMMU register, causing PCIe link instability, broken doorbells, inaccessible memory windows, bad RAS reporting, or VF isolation failures.
- `_BASE_IDX` drift is as risky as numeric offset drift. The same offset with the wrong base index can address a different aperture.
- The repeated VF config-space blocks are intentionally similar; copy-generation mistakes may only affect one VF and can be missed if tests exercise only VF0.
- Several names alias the same numeric offset, especially PCI/DPA/MSI fields and packed capability registers. Consumers must use the correct mask/shift definitions for the selected semantic view.
- RAS and parity status/counter registers may be write-one-to-clear or otherwise side-effectful in the real hardware. Read/write tests must avoid destructive probing unless the ASIC spec allows it.
- Doorbell access and self-ring aperture registers affect command submission and interrupt paths. Bad programming can look like unrelated engine hangs.
- IOMMU L2 control and error-rule registers can affect address translation behavior; changes should be validated under DMA, ATS/PASID, and SR-IOV workloads.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build coverage for AMDGPU configurations that compile `nbio_v7_9.c` and `amdgpu_ras_nbio_v7_9.c`; missing or renamed macros should fail compilation.
- Boot/probe on an NBIO 7.9.0 ASIC with clean `dmesg`, successful PCIe enumeration, correct BAR sizing, and successful `amdgpu` device initialization.
- Doorbell smoke tests: graphics/compute queue submission, SDMA copies, VCN operation, and interrupt handling after `nbio_v7_9_*_doorbell_range()` programs the S2A and BIF doorbell registers.
- SR-IOV tests with multiple VFs, not just VF0: VF config-space visibility, MSI/MSI-X operation, ATS/ARI capability behavior, VF mailbox traffic, HDP flush completion, and VF doorbell/FB access status.
- RAS tests or fault-injection on supported hardware: parity status/counter visibility, RAS global status changes, and correct IRQ registration through the NBIO RAS manager.
- PCIe stress: link retrain/speed checks, AER status logging, lane equalization/margining visibility, and reset/FLR behavior.
- IOMMU/ATS/PASID DMA workloads to detect incorrect L2 and translation-related offsets.
- Register audit scripts comparing generated offsets and `_BASE_IDX` values against the authoritative ASIC register database for NBIO 7.9.0.

### subset-b-003326: lines 9164-10004

# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_9_0_offset.h lines 9164-10004

## Scope

This chunk is the tail of the generated AMD NBIO 7.9.0 register offset header. It contains C preprocessor constants only: 361 register-offset macros and 361 matching `_BASE_IDX` macros, followed by the closing header guard. The requested range begins in the VF0 RCC block and then covers the repeated virtual-function register windows for VF1 through VF7.

The content is source-tree-aligned with AMDGPU's `drivers/gpu/drm/amd/include/asic_reg/nbio` generated register database. It does not define executable code, structs, enums, allocation paths, callbacks, or locks.

## Purpose and Register Families

The macros identify NBIO/BIF/RCC register addresses for SR-IOV endpoint function `DEV0_EPF0` virtual functions. They are used by AMDGPU SOC15 register access helpers to compute MMIO offsets for NBIO 7.9.0 hardware.

The covered address blocks are:

- VF0 RCC `BIFDEC2` MSI-X tail: `regRCC_DEV0_EPF0_VF0_GFXMSIX_VECT{0..3}_*` and `regRCC_DEV0_EPF0_VF0_GFXMSIX_PBA`.
- VF1 through VF7 `BIFPFVFDEC1`: BIF bus-master/atomic status, doorbell self-ring GPA aperture base/control, HDP coherency flush/invalidate controls, GPU HDP flush request/done, BIF transaction pending, NBIF graphics address LUT bypass, and mailbox transmit/receive/control/interrupt registers.
- VF1 through VF7 `SYSPFVFDEC`: indexed MMIO access registers `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI`.
- VF1 through VF7 RCC `BIFPFVFDEC1`: RCC error log, doorbell aperture enable, configured memory size/reserved registers, and IOV function identifier.
- VF1 through VF7 RCC `BIFDEC2`: four MSI-X vector table entries with address low/high, message data, control, and the pending-bit array register.

The repeated VF blocks intentionally share the same per-function register offsets, while the macro names encode the virtual-function number. `_BASE_IDX` selects the NBIO address-base slot used by the SOC15 register-offset machinery.

## Important APIs, Types, and Macros

This header exposes generated register-address macros in the AMDGPU naming convention:

- `regBIF_BX_DEV0_EPF0_VF<n>_*` for BIF virtual-function registers.
- `regRCC_DEV0_EPF0_VF<n>_*` for RCC virtual-function registers, including MSI-X table/PBA registers.
- `*_BASE_IDX` companions that tell `SOC15_REG_OFFSET()` and `RREG32_SOC15`/`WREG32_SOC15` style helpers which base-index table entry to apply.

The constants are not public APIs by themselves. They are consumed by NBIO and RAS code that includes `nbio/nbio_7_9_0_offset.h`, most directly `amdgpu/nbio_v7_9.c` and `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`. A concrete integration point in `nbio_v7_9_set_reg_remap()` uses `regBIF_BX_DEV0_EPF0_VF0_HDP_MEM_COHERENCY_FLUSH_CNTL` via `SOC15_REG_OFFSET()` to choose the HDP flush register remap location for SR-IOV VF or large-page configurations.

The companion `nbio_7_9_0_sh_mask.h` supplies bit shifts and masks for field-level operations. This `*_offset.h` file only identifies register locations.

## Control Flow and Data Flow

There is no control flow inside this chunk. Runtime behavior is indirect:

1. AMDGPU selects NBIO 7.9.0 support for a device generation and includes this generated header.
2. Driver code names a register macro and passes it to a SOC15 helper such as `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, or an extended instance-aware variant.
3. The helper combines the register offset with the macro's `_BASE_IDX`, NBIO instance information, and the device's MMIO base mapping.
4. Reads and writes then interact with hardware state such as doorbell aperture control, HDP coherency, mailbox buffers, transaction-pending status, or MSI-X vector state.

The data represented here is address metadata. Hardware supplies or consumes the actual register values. For example, HDP flush request/done registers coordinate cache coherency with the host data path, mailbox registers carry PF/VF or VM/HV communication words, and MSI-X table/PBA registers describe interrupt delivery state for each virtual function.

## State and Persistence

The header itself has no mutable software state and no persistence. Its constants are fixed at compile time.

The state addressed by these macros persists in hardware or PCIe configuration/MMIO-visible register space according to the NBIO reset and power domains:

- Doorbell aperture base/control and RCC doorbell enable registers affect how a VF's doorbell MMIO range is exposed and routed.
- HDP coherency and GPU HDP flush request/done registers represent synchronization with memory-visible GPU/CPU data paths.
- Mailbox transmit/receive/control/interrupt registers hold communication state between the VF-facing BIF path and management or virtualization components.
- `BIF_TRANS_PENDING`, error logs, BME status, and atomic error logs expose transient hardware status that may be asynchronously updated by the device.
- MSI-X vector address/data/control and PBA registers reflect interrupt-table state for each VF and must match PCI/MSI-X expectations.

Because these are generated address constants, an incorrect value becomes a systematic runtime hardware access bug wherever the macro is used.

## Dependencies and Integration Points

This chunk depends on the AMDGPU SOC15/NBIO register access framework and the generated NBIO 7.9.0 register database layout. It integrates with:

- `amdgpu/nbio_v7_9.c`, which includes this header for NBIO initialization, register remapping, doorbell setup, clock-gating controls, and HDP flush register location logic.
- `ras/ras_mgr/amdgpu_ras_nbio_v7_9.c`, which includes the offset and shift/mask headers while wiring NBIO RAS interrupt sources, even though the file's current handlers are dummy registration hooks.
- `nbio_7_9_0_sh_mask.h`, used with this offset file for field extraction and update.
- AMDGPU SR-IOV paths, where PF and VF register windows differ and VF-specific HDP/doorbell/mailbox/MSI-X offsets must resolve correctly.
- PCIe/MSI-X and virtualization semantics for BME, atomic operations, mailboxes, doorbells, function identifiers, and pending interrupts.

The chunk also mirrors similar generated VF blocks in other NBIO/NBIF generation headers, which is a useful cross-check but not a substitute for the NBIO 7.9.0 hardware register specification.

## Risks and Edge Cases

- The range starts at line 9164, just after most of VF0's BIF/RCC PFVF decode registers. Merge/reconciliation should treat this as a chunk boundary: VF0's HDP and mailbox definitions are in the preceding chunk, while VF0's MSI-X RCC tail is here.
- `_BASE_IDX` values are as important as the raw offsets. A correct register number with the wrong base index can access the wrong NBIO aperture.
- VF1 through VF7 are highly repetitive. Generated copy/paste or table-generation errors would likely affect only one VF number and may not appear unless that VF is enabled under SR-IOV.
- Doorbell aperture and HDP coherency registers are synchronization-sensitive. Wrong offsets can break queue submission, host/GPU coherency, or interrupt progress without producing an obvious compile-time failure.
- Mailbox and VM/HV mailbox registers are virtualization-facing. Accessing the wrong VF mailbox can leak state across functions or prevent PF/VF coordination.
- MSI-X vector and PBA offsets must remain aligned with PCI/MSI-X table layout. Incorrect offsets can misroute interrupts, leave vectors masked, or corrupt pending-bit accounting.
- Status/log registers such as BME status, atomic error log, RCC error log, and transaction-pending are hardware-updated; driver code must respect their documented clear/read semantics from the hardware spec and companion masks.

## Test and Validation Signals

Validation is mostly compile-time and hardware-integration oriented:

- Build AMDGPU configurations that include `nbio_7_9_0_offset.h`; missing or renamed macros fail at compile time in NBIO/RAS users.
- Boot NBIO 7.9.0 hardware in PF mode and SR-IOV VF mode and verify `nbio_v7_9_set_reg_remap()` maps the HDP memory coherency flush register as expected.
- Exercise SR-IOV with multiple enabled VFs, not only VF0, and verify queue doorbells, HDP flush completion, and mailbox traffic for VF1 through VF7.
- Inspect MSI-X behavior per VF: vector programming, masking/unmasking, pending-bit updates, and interrupt delivery under load.
- Use PCIe/AER or device diagnostics to confirm BME status, atomic error logging, RCC error logging, and BIF transaction-pending registers report plausible values.
- Run suspend/resume, FLR, hot reset, and GPU reset paths to ensure VF doorbell, mailbox, HDP, and MSI-X state is either preserved or reinitialized by the owning driver/firmware path.
