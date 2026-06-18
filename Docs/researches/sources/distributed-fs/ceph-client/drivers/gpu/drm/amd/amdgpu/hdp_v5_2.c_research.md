# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/hdp_v5_2.c

## Purpose
`hdp_v5_2.c` implements HDP 5.2 behavior, with a custom flush path through KFD MMIO remap registers and clock/power gating logic for ATOMIC and RC memory blocks.

## Important APIs, Types, And Functions
The exported `hdp_v5_2_funcs` table provides `hdp_v5_2_flush_hdp`, `hdp_v5_2_update_clock_gating`, and `hdp_v5_2_get_clockgating_state`. Unlike v5.0, this table does not provide invalidate or init-register callbacks.

## Control Flow
`hdp_v5_2_flush_hdp` writes the remapped `KFD_MMIO_REMAP_HDP_MEM_FLUSH_CNTL` register either directly or through a command ring. Direct flush posts the write by reading back the remapped register on SR-IOV VF, but on bare metal avoids reading the remapped register and instead calls `nbio.funcs->get_memsize()` when available.

Clock gating forces ATOMIC/RC memory clocks on, disables all memory power-control bits, then enables the preferred single mode in priority order SD, LS, then DS according to `adev->cg_flags`. It sets ATOMIC and RC power-control enable bits before releasing clock overrides. Medium-grain gating toggles soft override masks in `regHDP_CLK_CNTL`; state reporting inspects those masks and the ATOMIC memory power mode bits.

## State, Dependencies, And Integration
State is in HDP 5.2 clock and memory-power registers plus remapped MMIO offsets in `adev->rmmio_remap`. Dependencies include HDP 5.2 headers, KFD MMIO remap constants, SOC15 register access, NBIO memsize callback, ring writes, SR-IOV helpers, and `adev->cg_flags`.

## Risks And Test Signals
Risks include incorrect remap offset arithmetic, unsafe readback of remapped flush registers, SR-IOV posting differences, and memory-power mode priority changes. Tests should exercise direct and ring HDP flush, SR-IOV VF behavior, KFD-visible memory coherency, and clock-gating state with LS/DS/SD combinations.
