# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/vector.c

## Purpose
This file owns x86 local APIC interrupt vector allocation and the root vector irqdomain. It assigns vectors to IRQs, composes APIC MSI messages, manages vector migration and cleanup during affinity changes, reserves legacy/system vectors, handles CPU online/offline vector state, and provides APIC/PIC debug dumps.

## Important APIs, Types, And Functions
`struct apic_chip_data` stores per-IRQ vector, previous vector, target CPU, previous CPU, IRQ number, cleanup linkage, and reservation/managed flags. Global state includes `x86_vector_domain`, `vector_lock`, `vector_searchmask`, `vector_matrix`, and per-CPU cleanup timers. Important functions include `lock_vector_lock()`, `unlock_vector_lock()`, `init_irq_alloc_info()`, `copy_irq_alloc_info()`, `irqd_cfg()`, `irq_cfg()`, `lapic_assign_legacy_vector()`, `lapic_update_legacy_vectors()`, `lapic_assign_system_vectors()`, `arch_early_irq_init()`, `lapic_online()`, `lapic_offline()`, `vector_schedule_cleanup()`, `irq_complete_move()`, `lapic_can_unplug_cpu()`, and the `x86_vector_domain_ops`.

## Control Flow
`arch_early_irq_init()` creates the `VECTOR` irqdomain, makes it default, allocates the vector matrix, and initializes IO-APIC early state. Allocation through `x86_vector_alloc_irqs()` creates `apic_chip_data`, sets the APIC irq chip, handles legacy vectors specially, and either assigns or reserves vectors according to managed/reservation policy. Activation assigns real vectors for reserved or managed IRQs. Affinity changes allocate a new vector under `vector_lock`, update per-CPU `vector_irq`, and mark the old vector for deferred cleanup. The first interrupt on the new vector calls `irq_complete_move()`, scheduling cleanup on the previous CPU; a timer frees the old vector after checking IRR.

## State And Persistence
The vector matrix tracks available, reserved, managed, legacy, and system vectors. Per-IRQ chip data persists until IRQ free. Per-CPU `vector_irq[]` maps vectors to descriptors or sentinel states. Cleanup state persists in per-CPU hlist/timer objects. System and legacy vector reservations are established at boot and CPU-online time.

## Dependencies And Integration Points
It depends on generic irqdomain/irq_matrix APIs, local APIC register access, IO-APIC state (`io_apic_irqs`, `gsi_top`), interrupt remapping selection, legacy PIC, MSI message composition, CPU hotplug, SMP vector cleanup, debugfs, and APIC tracepoints. IO-APIC and MSI code use `irqd_cfg()` and vector-domain parent allocation.

## Risks
Vector migration is race-prone: stale vectors must not be freed until the new vector receives an interrupt or cleanup proves no pending IRR. CPU hotplug fixups can leave stale vectors if move completion is mishandled. Exhaustion of vector space affects IRQ affinity and CPU unplug safety. Incorrect legacy vector handling can break timer/PIC fallback.

## Test Signals
Use IRQ allocation/free stress, MSI affinity changes under interrupt load, CPU hotplug, managed IRQs with isolated CPUs, vector exhaustion scenarios, `/proc/interrupts`, debugfs irqdomain output, APIC tracepoints, and boot APIC/PIC dumps with `show_lapic=`.
