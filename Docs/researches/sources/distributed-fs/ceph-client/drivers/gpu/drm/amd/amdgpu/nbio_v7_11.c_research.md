# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_11.c

## Purpose
`nbio_v7_11.c` supports NBIO 7.11 devices with PF1/BIF1 register layout, USB4-flavored PCIe control registers, VPE doorbell ranges, VCN0/1 doorbells, clock/light-sleep control, and a 0x44000 MMIO remap hole.

## Important APIs, Types, And Functions
The file exports `nbio_v7_11_hdp_flush_reg` and `nbio_v7_11_funcs`. Important callbacks include `vpe_doorbell_range()`, `vcn_doorbell_range()`, `sdma_doorbell_range()`, `enable_doorbell_selfring_aperture()`, `ih_control()`, `init_registers()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, `get_pcie_port_index_offset()`, and `set_reg_remap()`.

## Control Flow
Common init programs PF1-oriented remap/PCIe offsets, sets request-size fields, clears a strap bit for NBIO 7.11.0 through 7.11.4, remaps HDP flush registers, and enables doorbells. Doorbell paths use PCIe-port reads/writes for CSDMA, VPE/VPE1, VCN0/VCN1, and IH ranges. Clock gating writes the BIF_BIF256_CI256_RC3X4_USB4 CPM register; light sleep writes PCIe CNTL2 and TX_POWER_CTRL_1.

## State And Persistence
The code mutates PF1 HDP flush, PCIe port, BIF1 interrupt, doorbell self-ring, and request-size registers. State persists only until reset.

## Dependencies And Integration Points
It depends on generated NBIO 7.11 headers, KFD remap offsets, SOC15 register macros, and common NBIO dispatch. The header declares a `nbio_v7_11_ras_funcs` object, but this C file only defines the base function and flush tables.

## Risks
PF1 register naming makes accidental use of PF0 offsets a high-risk class. The VPE callback is additional surface compared with earlier versions. The header's RAS declaration appears stale or externally satisfied; a build configuration expecting it from this file would fail.

## Test Signals
Test CSDMA, VPE, VCN0/1, and IH doorbell operation; verify PF1 HDP flush masks; check BIF1 interrupt setup; and ensure NBIO 7.11.x strap clearing does not regress reset.
