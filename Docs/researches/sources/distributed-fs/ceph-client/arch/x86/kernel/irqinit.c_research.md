# sources/distributed-fs/ceph-client/arch/x86/kernel/irqinit.c

## Purpose
Initializes x86 interrupt vector mappings, ISA IRQ chip setup, per-CPU IRQ stacks, and final architecture IRQ gate/vector setup.

## Important APIs And State
Defines per-CPU `vector_irq` initialized to `VECTOR_UNUSED`; functions `init_ISA_irqs()`, `init_IRQ()`, and `native_init_IRQ()`.

## Control Flow
`init_ISA_irqs()` initializes BSP APIC virtual wire mode, initializes the legacy PIC, and assigns legacy IRQ descriptors to the PIC chip and level handler. `init_IRQ()` seeds CPU0 vector slots for ISA IRQ vectors, initializes this CPU's IRQ stack, and calls `x86_init.irqs.intr_init()`. `native_init_IRQ()` runs pre-vector quirks, completes FRED exception setup when configured, installs IDT APIC/IRQ gates if not using FRED, assigns LAPIC system vectors, and requests cascade IRQ2 when no IO-APIC/OpenFirmware IO-APIC is present.

## Dependencies And Integration Points
Depends on `legacy_pic`, APIC/LAPIC setup, IDT/FRED setup, `x86_init` platform hooks, IRQ stack initialization from arch-specific files, ACPI/OF IO-APIC discovery, generic IRQ descriptors, and vector allocator state consumed by `irq.c`.

## Risks And Test Signals
Risks include wrong legacy vector seeding, missing IRQ stack, FRED/IDT split mistakes, cascade IRQ request failure, and platform quirk ordering. Tests include boot on PIC-only, IO-APIC, OF IO-APIC, FRED and non-FRED systems, CPU0 ISA IRQ delivery, cascade IRQ2 presence, and early interrupt vector handling.
