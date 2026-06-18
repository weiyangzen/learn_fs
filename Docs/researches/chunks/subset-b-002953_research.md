# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_4_3_0_offset.h lines 1-2670

## Scope

This chunk is the opening section of the generated AMD NBIO 4.3.0 offset header. It covers the license/header guard and the first 69 `addressBlock` groups, from `nbio_nbif0_bif_bx_SYSDEC` through the start of `nbio_pcie0_pswuscfg0_cfgdecp`. Within lines 1-2670 there are 2,338 preprocessor definitions: 1,225 register/config address macros and 1,113 matching `_BASE_IDX` macros. The base-index distribution is 57 macros for base index 0, 90 for index 1, 677 for index 2, and 289 for index 3.

The file is data-only C preprocessor material. It defines no functions, structs, enums, storage, locks, allocation behavior, or direct MMIO operations. Its public interface is the generated offset convention:

- `reg<NAME>` or `cfg<NAME>` gives a register or PCI configuration-space offset/address.
- `reg<NAME>_BASE_IDX` identifies which NBIO base segment is combined with the offset by `NBIO_BASE()`, `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, and related helpers.

## Purpose

This header is the NBIO 4.3.0 register-address ABI for AMDGPU, display, and SMU code. NBIO covers PCIe/NBIF-facing control surfaces such as indirect PCIe access, firmware/driver/BIOS scratch registers, interrupt control, doorbell aperture routing, HDP coherency flushes, host memory access, PCIe link and ASPM/LTR programming, SR-IOV/PF/VF windows, MSI-X tables, mailbox registers, and PCIe configuration-space capabilities.

The companion `nbio_4_3_0_sh_mask.h` supplies bitfield shifts and masks for many of these addresses. Code normally uses this offset header with generated bitfield macros and AMDGPU helper APIs rather than hard-coded numeric offsets.

## Important Macro Families

### BIF_BX0 System Decode

The first block, `nbio_nbif0_bif_bx_SYSDEC`, defines the low-level NBIO/BIF system decode registers:

- `regBIF_BX0_PCIE_INDEX`, `regBIF_BX0_PCIE_DATA`, `regBIF_BX0_PCIE_INDEX2`, `regBIF_BX0_PCIE_DATA2`, and high-index variants expose indirect PCIe register access windows.
- `regBIF_BX0_SBIOS_SCRATCH_*`, `regBIF_BX0_BIOS_SCRATCH_*`, `regBIF_BX0_DRIVER_SCRATCH_*`, and `regBIF_BX0_FW_SCRATCH_*` define shared scratch register slots used for firmware, BIOS, driver, and display handoff state.
- `regBIF_BX0_BIF_RLC_INTR_CNTL`, `regBIF_BX0_BIF_VCE_INTR_CNTL`, and `regBIF_BX0_BIF_UVD_INTR_CNTL` expose engine interrupt controls.
- `regBIF_BX0_GFX_MMIOREG_CAM_ADDR*`, matching remap addresses, and CAM control/completion registers describe a GFX MMIO register remap/CAM aperture.

These early macros are especially visible to display resource code. `dcn32_resource.c` and `dcn321_resource.c` include this header and build `NBIO_SR()` entries from `regBIF_BX0_BIOS_SCRATCH_3`, `regBIF_BX0_BIOS_SCRATCH_6`, and their base-index macros.

### RCC Downstream, Endpoint, and Root-Complex Controls

The `rcc_dwn`, `rcc_dwnp`, `rcc_ep`, and `rcc_dev0` blocks define PCIe-facing control/status surfaces:

- Downstream and downstream-port blocks include PCIe reserved/scratch/control/config/RX/bus/strap registers, link-speed controls, LTR message state, and error controls.
- Endpoint block macros include endpoint PCIe scratch/control/interrupt/status, bus/config controls, transmit LTR control, DPA capabilities and substate power-allocation aliases, PME control, TX requester ID, error/RX controls, and link-speed control.
- Root-complex device macros include RAS/error interrupt control, BACO, reset enable, vendor-defined-message support, margining parameters, GPU IOV region and HostVM enable, console IOV mode and VF layout, peer register ranges, bus/config aperture sizing, XDMA ranges, feature controls, bus number lists, captured host bus number, peer framebuffer offsets, device/function lists, link controls, endpoint requester-ID restore, LTR switch control, and multi-host arbitration.

`nbio_v4_3.c` uses these address definitions to read strap revision ID, program LTR and ASPM paths, control memory access, and initialize NBIO state.

### PF, VF, and Indirect Access Windows

`nbio_nbif0_bif_bx_pf_SYSPFVFDEC` and each VF `SYSPFVFDEC` block define `MM_INDEX`, `MM_DATA`, and `MM_INDEX_HI` style indirect MMIO access windows. The PF block also defines `RSMU_INDEX`, `RSMU_DATA`, and `RSMU_INDEX_HI`, which `nbio_v4_3_get_pcie_index_offset()` and `nbio_v4_3_get_pcie_data_offset()` expose through the NBIO function table.

The presence of both PF and per-VF indirect windows is important for SR-IOV. It lets PF-owned and VF-owned code paths address different windows while still sharing the same generated macro naming convention.

### BIF_BX0 Core BIF Controls

The `nbio_nbif0_bif_bx_BIFDEC1` block defines core NBIO/BIF controls:

- Strap and pinstrap registers such as `regBIF_BX0_CC_BIF_BX_STRAP0` and `regBIF_BX0_CC_BIF_BX_PINSTRAP0`.
- Indirect access and bus controls such as `regBIF_BX0_BIF_MM_INDACCESS_CNTL`, `regBIF_BX0_BUS_CNTL`, and BIF scratch registers.
- Reset and interrupt controls including `regBIF_BX0_BX_RESET_EN`, `regBIF_BX0_BX_RESET_CNTL`, `regBIF_BX0_INTERRUPT_CNTL`, and `regBIF_BX0_INTERRUPT_CNTL2`.
- Doorbell and framebuffer enable registers such as `regBIF_BX0_BIF_DOORBELL_CNTL`, `regBIF_BX0_BIF_DOORBELL_INT_CNTL`, and `regBIF_BX0_BIF_FB_EN`.
- Transaction pending, memory type, NBIF GFX address LUT, HDP remap flush controls, BIF ring-buffer pointers, and MP1 interrupt control.

`nbio_v4_3.c` uses this family for HDP remap programming, MC framebuffer access enable/disable, IH interrupt setup, and register-remap base selection.

### MSI-X, Strap, GDC, and PF BIFPFVF Blocks

`nbio_nbif0_rcc_dev0_epf0_BIFDEC2` defines four GFX MSI-X vector table entries, each with low/high address, message data, and control registers, plus an MSI-X pending-bit array (`GFXMSIX_PBA`). The same table shape reappears for each VF.

`nbio_nbif0_rcc_strap_BIFDEC1` lists BIF, port, and endpoint-function strap registers. These are persistent hardware configuration inputs or latched strap states. Driver code reads selected strap fields to derive revision, link, or power-management policy.

`nbio_nbif0_bif_bx_pf_BIFPFVFDEC1` defines PF-visible BME status, atomic error logging, self-ring doorbell aperture base/control, HDP coherency flush and invalidate controls, GPU HDP flush request/done, transaction-pending, and NBIF GFX address LUT bypass registers. `nbio_v4_3_get_hdp_flush_req_offset()`, `nbio_v4_3_get_hdp_flush_done_offset()`, and `nbio_v4_3_enable_doorbell_selfring_aperture()` are direct consumers of this surface.

`nbio_nbif0_rcc_dev0_epf0_BIFPFVFDEC1[13440..14975]` defines EPF0 RCC error log, doorbell aperture enable, config memory size, config reserved, and IOV function identifier registers. `nbio_v4_3_get_memsize()` reads `regRCC_DEV0_EPF0_RCC_CONFIG_MEMSIZE`, and `nbio_v4_3_enable_doorbell_aperture()` uses the associated doorbell aperture enable field.

`nbio_nbif0_gdc_GDCDEC` contributes a smaller GDC group: SHUB interface control, NBIF GFX doorbell status, ATDMA miscellaneous control, and S2A miscellaneous control.

### VF0 Through VF15 Repeated Register Windows

The largest portion of this chunk is the repeated VF0 through VF15 layout. Each VF has three block shapes:

- `bif_bx_dev0_epf0_vfN_BIFPFVFDEC1` with BME status, atomic error log, self-ring doorbell aperture base/control, HDP register/memory coherency flush controls, flush-only and invalidate-only controls, GPU HDP flush request/done, transaction-pending status, NBIF GFX address LUT bypass, transmit and receive mailbox data dwords, mailbox control, mailbox interrupt control, and `BIF_VMHV_MAILBOX`.
- `bif_bx_dev0_epf0_vfN_SYSPFVFDEC` with VF indirect MM index/data/high-index registers.
- `rcc_dev0_epf0_vfN_BIFPFVFDEC1` and `rcc_dev0_epf0_vfN_BIFDEC2` with VF RCC error/config/doorbell/IOV identity registers and four MSI-X vector entries plus PBA.

The repeated offsets are intentionally identical across VFs while the macro names encode the VF number. This provides compile-time names for per-VF management without requiring callers to hand-calculate register names. The pattern also means mechanical generator errors can affect all VFs in the same way.

### PCIe Config-Space Block Start

The final covered block starts `nbio_pcie0_pswuscfg0_cfgdecp` at base address `0xfffe00000000`. Unlike the earlier `reg*` macros, this block uses `cfgPSWUSCFG0_0_*` macros with absolute-looking PCIe configuration-space addresses. Covered entries include:

- Standard config header fields: vendor/device ID, command/status, revision/class, cache line, latency, header type, BIST, bus-number windows, IO/memory/prefetchable base/limit registers, ROM base, and interrupt line/pin.
- Capability registers for vendor-specific, power-management, PCIe, MSI, SSID, virtual channel, device serial number, advanced error reporting, secondary PCIe, ACS, and multicast capability structures.
- Link, device, lane equalization, AER header/TLP-prefix log, and multicast address registers.

The chunk ends in this PCIe config block at `cfgPSWUSCFG0_0_PCIE_MC_ADDR1`; later config entries continue outside the requested range.

## Control Flow and State Behavior

There is no executable control flow in this header. All behavior is compile-time name binding: C code includes the header, picks a generated macro, combines it with a base index, and issues reads/writes through AMDGPU MMIO or config-space helpers.

The state described by this chunk is persistent hardware state, not in-memory driver state. Examples include BIOS/driver/firmware scratch contents, PCIe link and endpoint state, interrupt routing, BIF reset state, doorbell aperture bases and enables, HDP flush request/done state, transaction-pending bits, VF mailbox contents, MSI-X vector programming, strap-derived configuration, PCIe capability registers, and config-space error/status latches.

Several registers are command-like or status-like rather than durable configuration. HDP flush request/done, coherency flush-only/invalidate-only controls, interrupt status/control, transaction-pending, mailbox valid/ack state, MSI-X PBA bits, AER status/log fields, and scratch registers need ordering and polling discipline from the owning driver code. The offset header does not encode those semantics.

## Dependencies and Integration Points

This chunk depends on the broader generated NBIO 4.3.0 header set:

- `nbio_4_3_0_sh_mask.h` supplies field shifts and masks for many registers named here.
- SOC15/NBIO helper macros such as `NBIO_BASE()`, `SOC15_REG_OFFSET()`, `RREG32_SOC15()`, `WREG32_SOC15()`, `WREG32_FIELD15_PREREG()`, `REG_SET_FIELD()`, and `REG_GET_FIELD()` consume the generated names.
- `amdgpu/nbio_v4_3.c` is the direct NBIO implementation consumer. It reads/writes registers for HDP remap, revision ID, framebuffer access, memory size, SDMA/VCN/IH/GC doorbell windows, self-ring doorbell aperture, interrupt control, clock gating, light sleep, HDP flush offsets, RSMU indirect access offsets, register remap, ASPM/LTR, and SR-IOV function-table variants.
- `amdgpu_discovery.c` selects `nbio_v4_3_funcs`, `nbio_v4_3_sriov_funcs`, and `nbio_v4_3_hdp_flush_reg` for matching hardware, so these offsets are part of runtime ASIC discovery wiring.
- `gmc_v11_0.c`, `gfx_v11_0.c`, `sdma_v6_0.c`, `sdma_v7_0.c`, and `sdma_v7_1.c` include `nbio_v4_3.h` and indirectly rely on the NBIO function table backed by these offsets.
- `pm/swsmu/smu13/smu_v13_0_0_ppt.c` and `smu_v13_0_7_ppt.c` include this offset/mask pair for SMU power-management policy.
- `display/dc/resource/dcn32/dcn32_resource.c` and `dcn321_resource.c` include this header to populate NBIO scratch-register addresses used by display resource code.

## Risks

- Offset drift is high impact. A wrong numeric value or `_BASE_IDX` can direct reads/writes to a different NBIO aperture, corrupting PCIe, doorbell, interrupt, HDP flush, or VF state.
- The PF/VF repetition is vulnerable to mechanical mistakes. VF0-VF15 blocks have near-identical offset values with different macro names; a missing VF, swapped suffix, or wrong base index could break SR-IOV isolation or VF interrupt/mailbox routing.
- Doorbell aperture and self-ring doorbell registers are security and stability sensitive. Wrong base, size, mode, or enable values can expose an incorrect GPA window or make ring doorbells stop working.
- HDP coherency and flush registers are ordering-sensitive. Incorrect request/done offsets or coherency flush controls can leave CPU-visible or GPU-visible memory stale.
- Mailbox and VM/HV registers are protocol-sensitive. Offsets alone do not express valid/ack sequencing, interrupt enables, or ownership; misuse can wedge PF/VF communication.
- MSI-X table and PBA offsets must match PCIe expectations. Incorrect vector address/data/control mapping can break interrupts or leave vectors masked/pending incorrectly.
- PCIe ASPM/LTR and link-control registers interact with platform policy. Bad offsets or field pairing can cause link instability, resume failures, or poor power behavior.
- Scratch registers are shared with firmware/BIOS/display paths. Treating them as private storage risks clobbering handoff state.
- The final PCIe config block is partial in this chunk. File-level conclusions about `cfgPSWUSCFG0_0_*` must be reconciled with later chunks.

## Test and Validation Signals

Useful validation signals are mostly compile-time integration and hardware bring-up:

- Build AMDGPU, SMU13, and DCN32/DCN321 code paths that include `nbio_4_3_0_offset.h` and `nbio_4_3_0_sh_mask.h`; this catches missing or renamed generated macros.
- Exercise `nbio_v4_3_funcs` on matching ASICs through discovery, probing, suspend/resume, and remove paths.
- Verify HDP flush request/done offsets by running graphics, compute, SDMA, and KFD workloads that depend on CPU/GPU coherency.
- Test doorbell programming for SDMA, VCN, IH, GC, and self-ring apertures; confirm rings advance and interrupts are delivered.
- In SR-IOV environments, validate VF0-VF15 mailbox, MSI-X, doorbell, and HDP flush paths with multiple VFs active.
- Check display initialization on DCN32/DCN321 systems, especially BIOS scratch register use for display handoff.
- Exercise SMU13 power-management flows that include this NBIO header, including ASPM/LTR, clock gating, and light sleep transitions.
- Validate PCIe error and capability handling through AER/status inspection and link retraining or ASPM test coverage.

## Cross-Chunk Notes

The requested range starts at the file header and ends inside the `cfgPSWUSCFG0_0_*` PCIe configuration-space block. Earlier sections are complete enough to describe the BIF/RCC/PF/VF groups, but the PCIe config block continues beyond line 2670. The final per-file reconciliation should merge this chunk with later chunks before making source-file-level claims about the full NBIO 4.3.0 config-space map.
