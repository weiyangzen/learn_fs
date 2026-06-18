# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/amdgpu/ih_v6_1.c

## Purpose
`ih_v6_1.c` implements the IH block for OSSSYS/IH 6.1-era hardware. It mirrors the v6.0 lifecycle while using 6.1 register definitions, a larger primary ring, early IRQ domain setup, and slightly different overflow/toggle behavior.

## Important APIs, Types, And Functions
The exported object is `ih_v6_1_ip_block`. Core functions are `ih_v6_1_init_register_offset`, `force_update_wptr_for_self_int`, `ih_v6_1_toggle_ring_interrupts`, `ih_v6_1_enable_ring`, `ih_v6_1_irq_init`, `ih_v6_1_get_wptr`, `ih_v6_1_set_rptr`, `ih_v6_1_self_irq`, lifecycle callbacks, and clock/memory power-gating helpers.

## Control Flow
Early init first calls `amdgpu_irq_add_domain`, then installs IH and self-IRQ callbacks. Software init registers the self IRQ, initializes ring0 at 256 KiB, initializes ring1 for dGPU, sets doorbells, maps register offsets, creates a PAGE_SIZE software IH ring, and calls `amdgpu_irq_init`. Hardware init disables rings, performs NBIO control, optionally enables GPA addressing, programs ring registers and doorbells, configures storm/flood handling and dGPU ring1 routing, enables bus mastering and interrupts, and turns on forced self-interrupt wptr updates.

## State And Persistence
Runtime state lives in `adev->irq` rings and hardware IH registers. Doorbell indices are based on `adev->doorbell_index.ih`. The file persists clockgating and SRAM powergating state in OSSSYS registers. Unlike v6.0, ring toggle enable does not perform the explicit overflow-clear pulse sequence, and init does not reset the per-ring `overflow` flag in the same loop.

## Dependencies And Integration Points
Dependencies include OSSSYS 6.1 offset/mask headers, SOC15 accessors, PSP indirect programming for SR-IOV, NBIO IH configuration hooks, PCI, amdgpu IRQ domains and source registration, and the generic IV decode helpers.

## Risks
The `ih_v6_1_ip_block` metadata sets `.major = 6`, `.minor = 0`, `.rev = 0` despite the v6.1 filename and functions, which may be intentional compatibility or a version-label risk. Overflow handling still advances rptr by 32 and can lose vectors under pressure. PAGE_SIZE software ring sizing should be validated against interrupt burst behavior. TODO idle/reset callbacks remain placeholders.

## Test Signals
Test signals include probe on IH 6.1 hardware, IRQ domain registration, ring0/ring1 interrupt delivery, software ring pressure, resume after suspend, SR-IOV VF PSP indirect register programming, interrupt storm throttling, and clock/power-gating toggles.
