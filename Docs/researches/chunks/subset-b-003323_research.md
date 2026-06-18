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
