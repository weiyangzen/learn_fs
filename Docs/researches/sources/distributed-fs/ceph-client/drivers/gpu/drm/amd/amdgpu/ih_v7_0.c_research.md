# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v7_0.c

## Purpose
`ih_v7_0.c` implements the IH block for OSSSYS/IH 7.0 and includes special handling for IP version 7.1.0. It manages interrupt rings, self-interrupt routing, storm control, retry CAM setup, and clock/SRAM power behavior.

## Important APIs, Types, And Functions
The exported object is `ih_v7_0_ip_block`. Important functions include `ih_v7_0_init_register_offset`, `ih_v7_0_toggle_ring_interrupts`, `ih_v7_0_enable_ring`, `ih_v7_0_setup_retry_doorbell`, `ih_v7_0_irq_init`, `ih_v7_0_get_wptr`, `ih_v7_0_set_rptr`, `ih_v7_0_self_irq`, lifecycle callbacks, and gating helpers. It defines local v7.1 register offsets for ring1 client config and `IH_CHICKEN`.

## Control Flow
Software init registers the IH self IRQ, allocates a 256 KiB primary ring, optional dGPU ring1, register offsets, and a software ring sized as `IH_SW_RING_SIZE` for OSSSYS 7.1.0 or PAGE_SIZE otherwise. Hardware init disables rings, runs NBIO control, chooses normal or v7.1 register addresses for GPA and ring1 routing, programs ring bases and controls, configures storm/flood throttling, then for v7.1.0 allocates a retry CAM doorbell at `(ih + 2) << 1`, enables `IH_RETRY_INT_CAM_CNTL`, marks `adev->irq.retry_cam_enabled`, and finally enables interrupts and forced self wptr updates.

## State And Persistence
State spans `adev->irq.ih`, `ih1`, `ih_soft`, `retry_cam_doorbell_index`, and `retry_cam_enabled`, plus persistent register state until reset/fini. `get_wptr` clears overflow and moves rptr to `wptr + 32` on overflow. `set_rptr` writes CPU rptr memory and doorbells, with SR-IOV rearm retries when doorbell writes are lost.

## Dependencies And Integration Points
Dependencies include OSSSYS 7.0 register headers, SOC15 register access, `amdgpu_ip_version`, PSP indirect paths, NBIO hooks, PCI bus mastering, IRQ registration, self-IRQ work scheduling, and generic IV decoders. v7.1 behavior integrates with retry interrupt CAM hardware.

## Risks
The hard-coded v7.1 register offsets are local to this file and must remain synchronized with register headers/specs. Retry CAM enablement adds state not disabled explicitly in `irq_disable`. Wrong software ring sizing for v7.1 may affect retry/self interrupt workloads. Placeholder idle/reset callbacks remain. Overflow recovery loses entries under pressure.

## Test Signals
Probe both OSSSYS 7.0 and 7.1.0 paths, including dGPU ring1 routing, retry CAM doorbell programming, SR-IOV rearm, storm/flood behavior, suspend/resume, software ring sizing, and interrupt overflow injection.
