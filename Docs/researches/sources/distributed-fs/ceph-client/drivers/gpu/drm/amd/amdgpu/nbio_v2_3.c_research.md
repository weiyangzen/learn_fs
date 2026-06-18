# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v2_3.c

## Purpose
`nbio_v2_3.c` implements NBIO 2.3 services for Navi-era devices. It handles register remap, revision/memory discovery, framebuffer access gating, SDMA and VCN doorbells, IH setup, BIF clock/light-sleep gating, ASPM/LTR programming, Navi PCIe link workarounds, doorbell interrupt clearing, and MMIO remap setup.

## Important APIs, Types, And Functions
The exported surfaces are `nbio_v2_3_hdp_flush_reg` and `nbio_v2_3_funcs`. Important callbacks include `nbio_v2_3_get_rev_id()`, `mc_access_enable()`, `get_memsize()`, `sdma_doorbell_range()`, `vcn_doorbell_range()`, `ih_control()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, `enable_aspm()`, `program_aspm()`, `apply_lc_spc_mode_wa()`, `apply_l1_link_width_reconfig_wa()`, and `clear_doorbell_interrupt()`.

## Control Flow
Hardware init programs PCIe request-size fields, applies optional link workarounds, programs ASPM when enabled by policy, remaps HDP flush registers, and enables doorbell apertures. Doorbell functions choose SDMA0-3 and MMSCH0/1 registers, then set offset and size fields. ASPM setup temporarily disables L0s/L1 and LTR, configures strap/timer/LTR capability registers, optionally programs LTR if the upstream path supports it, and then restores link inactivity settings.

## State And Persistence
The file writes PCIe/NBIO registers and `adev->rmmio_remap`. SR-IOV VFs force revision ID to zero and use a VF HDP coherency-flush register for remap. State is reset-scoped, not persistent.

## Dependencies And Integration Points
It depends on generated NBIO 2.3 headers, `amdgpu_device_should_use_aspm()`, PCI device removability for Thunderbolt timing, KFD remap constants, `dev_is_removable()`, and SOC15 indirect PCIe accessors.

## Risks
ASPM and LTR programming is hardware-sensitive and can affect link stability. SDMA instance selection assumes up to four SDMA doorbell registers. Navi10-specific link-width workarounds should not leak to later ASICs. Doorbell interrupt clearing only applies to NBIO `3.3.0`, so regressions may appear only on that IP.

## Test Signals
Look for clean Navi boot, correct `adev->rev_id`, working SDMA/VCN/IH interrupts, ASPM state transitions on suspend/resume, no stuck doorbell interrupt after reset, and PCIe link width/power traces matching expectations.
