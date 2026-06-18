# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/amdgpu_dm/amdgpu_dm_irq.h

## Purpose
`amdgpu_dm_irq.h` declares Display Manager IRQ management interfaces used by DC and AMDGPU DM setup/teardown code.

## Important APIs, types, and functions
It declares `amdgpu_dm_irq_init()`, `amdgpu_dm_irq_fini()`, `amdgpu_dm_irq_register_interrupt()`, `amdgpu_dm_irq_unregister_interrupt()`, `amdgpu_dm_set_irq_funcs()`, `amdgpu_dm_outbox_init()`, `amdgpu_dm_hpd_init()`, `amdgpu_dm_hpd_fini()`, and suspend/resume hooks.

## Control flow
The intended order is initialize IRQ tables, register DC handlers, install AMDGPU IRQ source functions, initialize HPD/outbox interrupts, suspend/resume sources around power transitions, unregister handlers, and finalize during teardown.

## State and persistence behavior
No state is defined here. Runtime state lives in DM handler tables and hardware/DC interrupt enablement.

## Dependencies and integration points
It includes `irq_types.h` for DAL/DC IRQ definitions and serves as the platform boundary between DC interrupt users and AMDGPU's Linux IRQ implementation.

## Risks and edge cases
Registration is documented as invalid from interrupt context. Unregistration must use the returned handler index. Resume is split into early HPDRX and late HPD phases, so PM ordering matters.

## Test signals
Build coverage, probe/remove, suspend/resume, HPD hotplug, and DC handler registration validate the header contract.
