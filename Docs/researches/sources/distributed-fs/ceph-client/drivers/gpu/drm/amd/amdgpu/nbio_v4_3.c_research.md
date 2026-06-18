# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v4_3.c

## Purpose
`nbio_v4_3.c` provides NBIO 4.3 operations for newer SOC21-style devices, including S2A doorbell routing, HDP remap, ROM offset lookup, BIF clock/light-sleep control, ASPM/LTR programming for selected PCIe IPs, SR-IOV no-op doorbell variants, and ATHUB RAS event interrupt registration/handling.

## Important APIs, Types, And Functions
Exports are `nbio_v4_3_hdp_flush_reg`, `nbio_v4_3_funcs`, `nbio_v4_3_sriov_funcs`, and `nbio_v4_3_ras`. Key callbacks include `gc_doorbell_init()`, `get_rom_offset()`, `program_aspm()`, `set_reg_remap()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, and the RAS functions around `nbio_v4_3_ras_err_event_athub_irq_funcs`.

## Control Flow
Normal init sets the remap hole, initializes soft-reset strap state for NBIO `4.3.0`, programs PCIe power management when the PCIE IP is `7.4.0` or `7.6.0`, remaps HDP flush registers, and enables doorbells. Doorbell programming is S2A based: SDMA instance 0 uses port 2, VCN uses ports 4/5, GC writes fixed entries, and IH uses port 1. SR-IOV ops keep read/control callbacks but replace doorbell programming with no-ops, leaving host control intact.

## State And Persistence
The code mutates NBIO registers, PCIe config-like registers, the MMIO remap fields, and `adev->nbio` interrupt descriptors. State is volatile across reset.

## Dependencies And Integration Points
It depends on generated NBIO 4.3 headers, SOC21 BIF interrupt IDs, `amdgpu_irq_add_id()`, KFD remap constants, RAS global ISR, and PCIe ASPM build configuration.

## Risks
Using the regular ops in SR-IOV would program guest-controlled doorbells that should be host-owned. RAS processing assumes BIF ring is disabled and uses status polling/clearing, so missed clear bits can cause repeated interrupts. ASPM only runs for selected PCIe IP versions and may silently do nothing elsewhere.

## Test Signals
Validate bare-metal and SR-IOV doorbell behavior separately, RAS ATHUB interrupt registration under SOC21 client IDs, VCN/SDMA ring progress, ROM offset reads, and ASPM/LTR behavior on supported PCIE IPs.
