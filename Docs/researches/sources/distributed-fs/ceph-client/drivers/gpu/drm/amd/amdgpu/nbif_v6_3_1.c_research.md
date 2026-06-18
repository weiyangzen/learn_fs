# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbif_v6_3_1.c

## Purpose
`nbif_v6_3_1.c` implements the NBIF/NBIO service table for NBIF 6.3.1-family hardware, including HDP flush remapping, revision and memory-size discovery, MC aperture enablement, doorbell routing for SDMA/VCN/GC/IH, interrupt host control, ASPM/LTR programming, ROM offset lookup, MMIO remap selection, and ATHUB RAS event interrupt handling.

## Important APIs, Types, And Functions
The exported `nbif_v6_3_1_hdp_flush_reg`, `nbif_v6_3_1_funcs`, and `nbif_v6_3_1_ras` objects are consumed by ASIC setup code through `struct amdgpu_nbio_funcs` and `struct amdgpu_nbio_ras`. Core callbacks include `get_rev_id`, `mc_access_enable`, `sdma_doorbell_range`, `vcn_doorbell_range`, `gc_doorbell_init`, `ih_doorbell_range`, `ih_control`, `program_aspm`, `get_rom_offset`, and `set_reg_remap`. The file has explicit alternate register definitions for IP version `7.11.4`, including GDC S2A doorbell and strap registers.

## Control Flow
During common hardware init, the selected NBIO ops call `set_reg_remap()`, `program_aspm()`, `init_registers()`, optional HDP remap, and doorbell aperture enablement. Doorbell callbacks program S2A entries with AWID/range/upper-address selectors: SDMA instance 0 uses port 2, VCN instances use ports 4/5, GC writes two fixed entries, and IH uses port 1. Runtime interrupt setup calls `init_ras_err_event_athub_interrupt()`, while the no-BIF-ring handler polls and clears the doorbell interrupt status before invoking global RAS handling.

## State And Persistence
State is MMIO-backed in NBIF/NBIO, PCIE, PCI config space, and `adev->rmmio_remap`. The self-ring aperture uses `adev->doorbell.base`. No disk persistence exists; settings survive only until GPU reset or driver teardown.

## Dependencies And Integration Points
The file depends on AMDGPU core device state, generated NBIF/PCIE register headers, KFD MMIO remap offsets, PCIe capability helpers, SOC21 BIF interrupt IDs, and RAS global ISR dispatch.

## Risks
IP `7.11.4` register special-casing is easy to miss and would send doorbells or strap reads to the wrong offsets. Empty clock-gating callbacks mean callers must not assume BIF MGCG/LS state changes are active. The ASPM path touches both PCI config and NBIF/PCIE registers, so bad LTR path assumptions can break link power management. The source snapshot also contains duplicated text in the self-ring aperture expression, a maintenance signal worth checking against upstream.

## Test Signals
Useful signals are successful GPU init, KFD HDP flush remap visibility, SDMA/VCN/GC/IH ring doorbells working, `lspci`/power traces showing expected ASPM/LTR behavior, and RAS ATHUB interrupts clearing without repeated storms.
