# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/nbio_v6_1.c

## Purpose
`nbio_v6_1.c` is the Vega10-era NBIO implementation for SOC15 common code. It supplies HDP flush offsets/masks, revision/memory-size reads, framebuffer access gating, SDMA/IH doorbell programming, interrupt host setup, BIF medium-grain clock gating/light sleep, PCIe request ordering setup, ASPM/LTR programming, and MMIO remap setup.

## Important APIs, Types, And Functions
The file exports `nbio_v6_1_hdp_flush_reg` and `nbio_v6_1_funcs`. Important callbacks are `nbio_v6_1_init_registers()`, `program_aspm()`, `update_medium_grain_clock_gating()`, `update_medium_grain_light_sleep()`, `get_clockgating_state()`, `ih_control()`, `enable_doorbell_selfring_aperture()`, and `set_reg_remap()`.

## Control Flow
Common init invokes register remap, PCIe ASPM setup, NBIO register init, optional HDP remap, and doorbell aperture enablement. The init path sets software max-read-request controls and disables slave ordering. Doorbell setup writes SDMA0/1 and IH range registers. Clock-gating callbacks read/modify/write PCIE SMN registers according to `adev->cg_flags`.

## State And Persistence
State is in NBIO/PCIE registers and `adev->rmmio_remap`. Doorbell self-ring writes the physical doorbell base into GPA aperture registers. There is no persistent storage.

## Dependencies And Integration Points
It depends on generated NBIO 6.1 headers, Vega10 enum definitions, KFD remap constants, SOC15 register macros, and PCIe ASPM build-time support.

## Risks
The implementation assumes two SDMA instances and no VCN callback. ASPM/LTR values are hard-coded for this generation. If `PAGE_SIZE` exceeds 4 KiB or SR-IOV is active, the remap path falls back to VF HDP coherency-flush offsets, affecting user MMIO exposure.

## Test Signals
Signals include Vega boot without NBIO init errors, correct HDP flush behavior, functioning SDMA/IH doorbells, BIF MGCG/LS flags matching register state, and suspend/resume without PCIe link failures.
