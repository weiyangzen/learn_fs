# sources/distributed-fs/ceph-client/arch/x86/kernel/irq_64.c

## Purpose
Initializes 64-bit x86 per-CPU hardirq stacks, optionally mapping them with guard pages when VMAP_STACK is enabled.

## Important APIs And State
Defines per-CPU `hardirq_stack_inuse`, visible page-aligned `irq_stack_backing_store`, and `irq_init_percpu_irqstack()`. Internal `map_irq_stack()` either vmap-maps the backing pages or uses direct per-CPU storage.

## Control Flow And Persistence
For VMAP_STACK, `map_irq_stack()` gathers the physical pages backing the per-CPU irq stack, maps them with `vmap()` as kernel pages, and stores the actual top-of-stack in `hardirq_stack_ptr` to avoid hot-path adjustment. Without VMAP_STACK it points directly at the per-CPU backing store top. Initialization is idempotent per CPU.

## Dependencies And Integration Points
Depends on per-CPU allocation, vmalloc/vmap, IRQ stack definitions, KASAN/VMAP_STACK configuration, and common interrupt entry code that consumes `hardirq_stack_ptr`.

## Risks And Test Signals
Risks include vmap allocation failure, missing guard pages when disabled, wrong top-of-stack offset, and reuse during CPU hotplug. Tests include 64-bit boot with VMAP_STACK on/off, KASAN configurations, interrupt stack overflow detection elsewhere, CPU hotplug, and high interrupt load.
