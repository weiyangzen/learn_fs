# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/nbio/nbio_7_0_default.h lines 14587-14865

## Scope

This chunk is the final section of the generated AMD NBIO 7.0 default-register header. It contains `#define` constants for reset/default values, not executable code. The covered range spans the tail of the `nbio_nbif0_rcc_ep_dev0_BIFDEC1` block and then complete default sets for downstream PCIe, RCC, BIF/BX PF, GDC, GFX MSI-X, and Syshub indirect MMIO blocks before the file's include guard closes.

The companion headers `nbio_7_0_offset.h`, `nbio_7_0_sh_mask.h`, and `nbio_7_0_smn.h` provide the register offsets and bit masks that make these defaults usable. Active NBIO v7.0 driver code includes this file from `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `pm/powerplay/hwmgr/smu10_inc.h`.

## Purpose

The constants document hardware reset expectations for NBIO 7.0 registers. Driver code mostly uses the offset and mask headers for live register programming, while this default header supplies authoritative reset values for generated register metadata, diagnostics, initialization comparisons, and ASIC-specific bring-up references.

The chunk covers several functional areas:

- PCIe endpoint/downstream capability defaults, including Dynamic Power Allocation and link-control defaults.
- RCC register-configuration and reset defaults for config windows, peer ranges, BACO control, requester ID restore, and bus-number tracking.
- BIF/BX PF defaults for framebuffer enable, doorbell apertures, HDP remap/coherency flush registers, mailbox registers, interrupt controls, reset controls, and BACO timers.
- GDC defaults for SDP ports, SDMA/IH/MMSCH doorbell ranges, ATDMA, and doorbell fencing.
- GFX MSI-X vector table defaults with vectors initially masked.
- Syshub indirect MMIO defaults for clock gating, QoS, client controls, scratch registers, and NIC400 fabric function-modifier registers.

## Important Macros and Register Groups

There are no functions, structs, enums, or typedefs in this range. The important API surface is the macro namespace:

- `mmEP_PCIE_*_DEFAULT` and `mmPCIE_F0_DPA_*_DEFAULT`: endpoint PCIe defaults for DPA capability, latency, substate power allocation, PME, TX/RX control, error control, and link speed.
- `mmDN_PCIE_*_DEFAULT` and `mmPCIE_*_DEFAULT`: downstream/downstream-port PCIe defaults. Notable defaults are `mmDN_PCIE_BUS_CNTL_DEFAULT == 0x00000080`, `mmPCIE_ERR_CNTL_DEFAULT == 0x00000500`, and zeroed link-control defaults.
- `mmRCC_*_DEFAULT`: RCC defaults. `mmRCC_RESET_EN_DEFAULT == 0x00008000`, `mmRCC_PEER_REG_RANGE0_DEFAULT` and `mmRCC_PEER_REG_RANGE1_DEFAULT` are `0xffff0000`, and most configuration, peer offset, and bus-number registers reset to zero.
- `mmBIF_*_DEFAULT`, `mmBUS_CNTL_DEFAULT`, `mmBX_*_DEFAULT`, and related PF constants: BIF/BX PF reset defaults. Nonzero defaults include `mmBX_RESET_EN_DEFAULT == 0x00010003`, `mmBIF_BUSY_DELAY_CNTR_DEFAULT == 0x0000003f`, the BACO exit timers, VDDGFX lower/upper windows, doorbell global apertures, HDP remap controls, GPUIOV config sizes, and pad controls.
- `mmBIF_DOORBELL_GBLAPER*_DEFAULT`: default global doorbell aperture windows. Aperture 1 starts with `0x80000780`/`0x000007fc`, and aperture 2 starts with `0x80000800`/`0x0000087c`.
- `mmREMAP_HDP_MEM_FLUSH_CNTL_DEFAULT` and `mmREMAP_HDP_REG_FLUSH_CNTL_DEFAULT`: default remap targets for HDP memory and register flush controls. `nbio_v7_0_remap_hdp_registers()` overwrites the live registers during driver initialization based on `adev->rmmio_remap`.
- `mmGPU_HDP_FLUSH_REQ_DEFAULT` and `mmGPU_HDP_FLUSH_DONE_DEFAULT`: default zeroed flush request/done state. `nbio_v7_0_hdp_flush_reg` maps the done bits for CP0-CP9 and SDMA0/1 in the live driver.
- `mmBIF_SDMA0_DOORBELL_RANGE_DEFAULT`, `mmBIF_SDMA1_DOORBELL_RANGE_DEFAULT`, `mmBIF_IH_DOORBELL_RANGE_DEFAULT`, and `mmBIF_MMSCH0_DOORBELL_RANGE_DEFAULT`: all reset to zero. `nbio_v7_0_sdma_doorbell_range()`, `nbio_v7_0_ih_doorbell_range()`, and `nbio_v7_0_vcn_doorbell_range()` program their `OFFSET` and `SIZE` fields at runtime.
- `mmGFXMSIX_VECT{0,1,2}_*_DEFAULT` and `mmGFXMSIX_PBA_DEFAULT`: MSI-X vector address/data defaults are zero, while each vector control default is `0x00000001`, consistent with a masked vector at reset.
- `ixSYSHUB_MMREG_IND_*_DEFAULT`: defaults for indirect Syshub registers. Notable values include QoS controls at `0x0000001e`, DMA client controls at `0x20200000`, `ixSYSHUB_MMREG_IND_SYSHUB_CG_CNTL_DEFAULT == 0x00082000`, `ixSYSHUB_MMREG_IND_SYSHUB_HP_TIMER_DEFAULT == 0x00000100`, and MGCG controls at `0x00000080`.

## Control Flow and Runtime Use

This header has compile-time-only behavior:

1. The include guard `_nbio_7_0_DEFAULT_HEADER` prevents duplicate macro definitions.
2. Preprocessor definitions bind register default names to literal 32-bit values.
3. Consumers include this header alongside `nbio_7_0_offset.h` and `nbio_7_0_sh_mask.h`.
4. Runtime code uses the matching `mm*` or `ix*` register names with `RREG32_*`, `WREG32_*`, `SOC15_REG_OFFSET`, and `REG_SET_FIELD` helpers.

The chunk itself has no branches, loops, side effects, or direct control transfer. Runtime control flow appears in consumers:

- `nbio_v7_0_remap_hdp_registers()` writes `mmREMAP_HDP_MEM_FLUSH_CNTL` and `mmREMAP_HDP_REG_FLUSH_CNTL`.
- `nbio_v7_0_mc_access_enable()` writes `mmBIF_FB_EN` using `BIF_FB_EN__FB_READ_EN_MASK` and `BIF_FB_EN__FB_WRITE_EN_MASK`.
- Doorbell setup functions program `mmBIF_SDMA0_DOORBELL_RANGE`, `mmBIF_SDMA1_DOORBELL_RANGE`, `mmBIF_IH_DOORBELL_RANGE`, and `mmBIF_MMSCH0_DOORBELL_RANGE`.
- `nbio_v7_0_ih_control()` programs `mmINTERRUPT_CNTL2` and fields in `mmINTERRUPT_CNTL`.
- `nbio_7_0_read_syshub_ind_mmr()` and `nbio_7_0_write_syshub_ind_mmr()` access the `ixSYSHUB_MMREG_IND_*` namespace through `mmSYSHUB_INDEX` and `mmSYSHUB_DATA`.
- `nbio_v7_0_update_medium_grain_clock_gating()` toggles Syshub MGCG enable bits at `ixSYSHUB_MMREG_IND_SYSHUB_MGCG_CTRL_SOCCLK` and `ixSYSHUB_MMREG_IND_SYSHUB_MGCG_CTRL_SHUBCLK`.

## State and Persistence Behavior

The macros are immutable compile-time constants. They do not persist state themselves. The state they describe is hardware register state after reset or default strap/configuration loading.

Live persistent effects occur only when consumers write the associated registers:

- HDP remap registers persist the selected MMIO remap offsets until reset or reprogramming.
- Doorbell range registers persist queue/interrupt aperture routing for SDMA, IH, and VCN/MMSCH blocks.
- `mmBIF_FB_EN` controls whether NBIO permits framebuffer reads and writes.
- MSI-X vector registers hold interrupt target addresses, data, and mask state.
- Syshub indirect registers hold clock-gating, QoS, and interconnect control state.
- Scratch and mailbox registers are default-zero storage/control windows; their content can be used by firmware, virtualization, or driver paths outside this chunk.

Because these values are defaults, driver code must not assume they remain unchanged after firmware, bootloader, SR-IOV PF/VF management, suspend/resume, runtime power management, or previous driver initialization has touched the hardware.

## Dependencies

Direct dependencies are minimal:

- C preprocessor support for include guards and `#define`.
- Register naming conventions shared with generated AMD ASIC headers.
- Companion NBIO 7.0 offset and mask headers for usable addresses and field layout.

Runtime consumers depend on the amdgpu SOC15 register access layer:

- `RREG32_SOC15`, `WREG32_SOC15`, `SOC15_REG_OFFSET` for NBIO MMIO access.
- `RREG32_PCIE`, `WREG32_PCIE` for PCIe/SMN-style register access where applicable.
- `REG_SET_FIELD` and generated `__SHIFT`/`__MASK` constants from `nbio_7_0_sh_mask.h`.
- `struct amdgpu_device` fields such as `rmmio_remap`, `rmmio_base`, `cg_flags`, `dummy_page_addr`, and SR-IOV state helpers in `amdgpu/nbio_v7_0.c`.

## Integration Points

Key integration points visible from this chunk and its consumers:

- NBIO IP block selection: `nbio_v7_0_funcs` exposes NBIO operations to the broader amdgpu driver and relies on registers whose defaults are listed here.
- KFD/HSA integration: HDP flush remap constants are rewritten using `KFD_MMIO_REMAP_HDP_MEM_FLUSH_CNTL` and `KFD_MMIO_REMAP_HDP_REG_FLUSH_CNTL`, allowing user queues and compute paths to reach flush controls through a remapped MMIO page.
- Interrupt handling: `mmINTERRUPT_CNTL`, `mmINTERRUPT_CNTL2`, IH doorbell range defaults, and GFX MSI-X defaults connect NBIO reset state to amdgpu interrupt setup.
- Doorbell routing: zero default ranges mean SDMA, IH, and MMSCH doorbells are disabled until the driver assigns aperture offsets and sizes.
- Power management: BACO timers, VDDGFX windows, CLKREQ/PERST/PX pad controls, Syshub MGCG defaults, and light-sleep related Syshub controls integrate with power-gating, clock-gating, and platform link-management paths.
- Virtualization/SR-IOV: PF/VF decode blocks, GPUIOV config sizes, BIF transaction-pending registers, mailbox message buffers, VMHV mailbox, and doorbell self-ring aperture controls are the default substrate for PF/VF isolation and communication.
- Fabric/interconnect tuning: Syshub QoS, CL control, and NIC400 function-modifier defaults describe baseline data-movement behavior between DMA/HST clients and the system fabric.

## Risks and Edge Cases

- Generated-header drift: default values must match the ASIC register database. A stale value can mislead diagnostics or bring-up code even if runtime code mostly writes explicit field values.
- Duplicate register names across address blocks and ASIC generations can cause accidental inclusion or macro collision problems. The include guard prevents duplicate inclusion of this file, but it does not protect against selecting the wrong NBIO generation header.
- Default-zero doorbell and mailbox registers are safe reset values, but treating zero as an initialized runtime configuration would disable doorbells or leave firmware/virtualization mailboxes unusable.
- HDP remap defaults (`0x385c` and `0x3858`) are overwritten by runtime remap setup. Tests or diagnostics that compare against defaults after initialization need to account for that intentional mutation.
- MSI-X vector control defaults are masked (`0x1`). Interrupt tests must program and unmask vectors before expecting delivery.
- Syshub indirect registers require index/data sequencing. Incorrect access ordering or concurrent index/data users can read or write the wrong Syshub register.
- Several defaults encode platform-sensitive timing or electrical behavior, such as BACO exit timers, pad controls, and clock-gating hysteresis. Small changes can cause resume, link training, or low-power-state failures that only appear on specific boards.
- Some live register state can be modified before the kernel driver by firmware or by an SR-IOV PF. The driver should read-modify-write fields where appropriate instead of blindly restoring reset defaults.

## Test Signals

Useful validation signals for this chunk are mostly integration and hardware-facing:

- Build coverage: compile amdgpu paths that include `nbio_7_0_default.h`, especially `amdgpu/nbio_v7_0.c`, `amdgpu/soc15.c`, and `smu10_inc.h`, with no macro redefinition or missing-symbol failures.
- Register table consistency: generated default names in this file should align one-to-one with matching `mm*`/`ix*` offsets in `nbio_7_0_offset.h` and matching field masks in `nbio_7_0_sh_mask.h` where fields exist.
- Boot/probe on NBIO 7.0 hardware: amdgpu should initialize NBIO, enable framebuffer access, configure IH and SDMA/VCN doorbells, and expose expected PCIe/interrupt behavior.
- HDP flush tests: CP and SDMA flush request/done paths should observe the `GPU_HDP_FLUSH_DONE` masks used by `nbio_v7_0_hdp_flush_reg`.
- Interrupt tests: MSI/MSI-X and IH handling should work after `nbio_v7_0_ih_control()` and doorbell range setup; vectors should not be assumed active at reset because vector control defaults are masked.
- Power-management tests: suspend/resume, BACO entry/exit, clock gating, and light sleep should be exercised because this chunk contains defaults for BACO timers, VDDGFX windows, Syshub MGCG, and pad controls.
- SR-IOV/virtualization tests: PF/VF mailbox, GPUIOV config-size, transaction-pending, and doorbell aperture behavior should be checked on virtualized configurations.
