# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v7_7.c

## Purpose
`nbio_v7_7.c` supports NBIO 7.7 devices with BIF1/BIF0 split register naming. It supplies HDP remap, PF0 flush masks, BIF1 framebuffer and interrupt control, CSDMA/VCN/IH doorbells, PCIe port offsets, request-size initialization, clock/light-sleep gating, and remap selection.

## Important APIs, Types, And Functions
Exports are `nbio_v7_7_hdp_flush_reg` and `nbio_v7_7_funcs`. Important callbacks are `nbio_v7_7_sdma_doorbell_range()`, `vcn_doorbell_range()`, `ih_control()`, `init_registers()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, `get_pcie_port_index_offset()`, and `set_reg_remap()`.

## Control Flow
Init sets BIF0 PCIe request-size controls and clears a strap bit for NBIO `7.7.0`. Doorbell callbacks use CSDMA and VCN0 GDC ranges, while IH writes the GDC0 IH range. Interrupt control uses BIF_BX1 registers. Clock gating writes BIF0 CPM control, and light sleep writes BIF0 PCIE_CNTL2 plus TX_POWER_CTRL_1.

## State And Persistence
State is volatile in NBIO/BIF/GDC registers and `adev->rmmio_remap`. Self-ring aperture uses PF0 doorbell GPA base registers.

## Dependencies And Integration Points
It depends on generated NBIO 7.7 headers, SOC15 register helpers, KFD remap constants, and common NBIO dispatch.

## Risks
The header declares `nbio_v7_7_ras_funcs`, but this C file does not define RAS functions in the snapshot. BIF0/BIF1 split use makes register selection error-prone. The SDMA callback uses a single CSDMA doorbell range, so it is not a generic multi-instance SDMA implementation.

## Test Signals
Test CSDMA, VCN, and IH doorbells; BIF1 interrupt dummy-read setup; clock/light-sleep flags; NBIO `7.7.0` reset strap behavior; and link-time behavior around RAS declarations.
