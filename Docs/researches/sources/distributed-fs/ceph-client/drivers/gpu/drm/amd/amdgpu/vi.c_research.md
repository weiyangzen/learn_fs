# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/vi.c

## Purpose
`vi.c` implements the common AMDGPU "Volcanic Islands" ASIC support layer. It provides shared register accessors, ASIC function callbacks, reset policy, clock setup, BIOS/ROM access, clock and power-gating controls, doorbell setup, video codec capability reporting, SR-IOV hooks, and per-chip IP block registration for Topaz, Tonga, Fiji, Polaris, VegaM, Carrizo, and Stoney families.

## Important APIs, Types, And Functions
The externally visible entry points are `vi_srbm_select()`, `vi_set_virt_ops()`, `vi_set_ip_blocks()`, and `legacy_doorbell_index_init()`. The file also installs a private `amdgpu_asic_funcs` table through `vi_common_early_init()`, including callbacks for BIOS reads, register reads, reset, clock programming, HDP flush/invalidate, PCIe counters, BACO support, and video codec queries. Register access helpers include `vi_pcie_rreg/wreg`, `vi_smc_rreg/wreg`, `cz_smc_rreg/wreg`, `vi_uvd_ctx_rreg/wreg`, `vi_didt_rreg/wreg`, and `vi_gc_cac_rreg/wreg`. Initialization is exposed to the IP framework through `vi_common_ip_funcs` and `vi_common_ip_block`.

## Control Flow
The AMDGPU device setup path calls `vi_set_ip_blocks()`, which selects an ordered list of IP blocks based on `adev->asic_type`, virtual-display state, DC support, SR-IOV VF status, and optional ACP support. The common IP block then runs `vi_common_early_init()`, where register accessor functions, ASIC callbacks, revision IDs, external revision IDs, and clock/power-gating flags are established. Hardware init programs golden registers, ASPM, and doorbell aperture state. Suspend/resume map to hardware fini/init, and late/software init attach SR-IOV mailbox IRQ state when applicable.

Reset flow chooses between BACO and PCI config reset in `vi_asic_reset_method()` and `vi_asic_reset()`. PCI config reset clears bus mastering, triggers config reset, polls `CONFIG_MEMSIZE`, restores bus mastering, and updates scratch engine-hung state. Clock programming for UVD/VCE uses AtomBIOS dividers, SMC registers, and timeout loops. ASPM programming is gated by policy and ASIC generation, then writes multiple PCIe/SMC/BIF registers and accounts for L1 substates and Polaris revision quirks.

## State And Persistence
The code mutates persistent in-memory device state such as `adev->asic_funcs`, register accessor callbacks, `adev->rev_id`, `adev->external_rev_id`, `adev->cg_flags`, `adev->pg_flags`, `adev->doorbell_index`, `adev->has_hw_reset`, and SR-IOV virtual settings. Hardware state is changed through MMIO/SMC/PCIe register writes for golden registers, clock dividers, ASPM, doorbell aperture, HDP flush/invalidate, clock gating, and ring-emitted HDP operations. BIOS reads temporarily modify ROM/VGA control registers and restore them before returning.

## Dependencies And Integration Points
This file sits at the center of the VI AMDGPU stack. It depends on generated ASIC register headers, AtomBIOS helpers, DPM/SMU services, PCI helpers, the AMDGPU IP block framework, display backends (`dm_ip_block`, DCE, VKMS), memory controllers (`gmc_v7_4`, `gmc_v8_*`), interrupt handlers, graphics/SDMA/UVD/VCE blocks, ACP when configured, and SR-IOV support in `mxgpu_vi`. Register read whitelisting supports debug/ioctl paths that expose only selected status/configuration registers.

## Risks
Most risk is hardware-sequencing risk: incorrect ASIC dispatch, revision mapping, clock-gating flags, or register offsets can hang devices or break power management. Indirect register access relies on spinlocks and readbacks; missed locking would corrupt index/data windows. ASPM programming is especially revision-sensitive and touches PCIe link behavior. `vi_read_bios_from_rom()` casts the BIOS buffer to `u32 *` and reads aligned dwords, so callers must provide suitable storage and size. `vi_common_get_clockgating_state()` sets `*flags = 0` for SR-IOV but continues reading registers, which is benign only if those reads are valid for the VF path.

## Test Signals
Useful signals are successful boot/probe across all VI ASIC types, absence of MMIO timeout or GPU reset errors, correct `amdgpu_device_ip_block_add()` order, successful UVD/VCE ring tests after clock programming, suspend/resume stability, BACO and PCI reset recovery, expected debug register reads, PCIe replay/usage counters, and power-management tests that verify clock-gating flags and ASPM behavior. SR-IOV should exercise mailbox IRQ attach/detach and virtual display paths.
