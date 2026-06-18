# sources/distributed-fs/ceph-client/arch/x86/kernel/apic/local.h

## Purpose
This private APIC header declares shared helpers used across the APIC subdirectory. It centralizes x2APIC helper declarations, IPI helper prototypes, local APIC logical initialization, and ICR preparation logic.

## Important APIs, Types, And Functions
It declares x2APIC functions (`x2apic_get_apic_id()`, `x2apic_send_IPI_all()`, `x2apic_send_IPI_allbutself()`, `x2apic_send_IPI_self()`), `x2apic_max_apicid`, and the `apic_use_ipi_shorthand` static key. `__prepare_ICR(shortcut, vector, dest)` constructs the APIC ICR low word, selecting fixed delivery by default and NMI delivery for `NMI_VECTOR`. Under `CONFIG_X86_X2APIC`, `__x2apic_send_IPI_dest()` writes x2APIC ICR MSRs. It also declares the common APIC LDR and default IPI helper functions.

## Control Flow
Driver files include this header to populate `struct apic` callbacks. IPI helpers call `__prepare_ICR()` before writing xAPIC or x2APIC ICRs. x2APIC drivers use `__x2apic_send_IPI_dest()` as their final send primitive.

## State And Persistence
The header owns no storage except declarations. Its inline helpers encode assumptions about ICR bit layout and delivery modes.

## Dependencies And Integration Points
It depends on `asm/irq_vectors.h`, `asm/apic.h`, and jump labels. It integrates `ipi.c`, `apic_common.c`, `x2apic_*`, `probe_32.c`, `apic_flat_64.c`, Numachip, and Secure AVIC driver code.

## Risks
Because `__prepare_ICR()` is shared by many send paths, a bug affects fixed and NMI IPI delivery broadly. The x2APIC inline write assumes callers apply any required WRMSR fences, which the x2APIC implementations do before calling it.

## Test Signals
Compile coverage across xAPIC/x2APIC and 32/64-bit configurations, IPI delivery tests, NMI sends, and APIC driver selection exercise this header indirectly.
