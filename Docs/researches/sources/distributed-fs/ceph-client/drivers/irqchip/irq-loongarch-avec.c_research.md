<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-avec.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-avec.c

## Purpose
Implements the LoongArch Advanced Vector Interrupt Controller, an MSI-capable vector allocator and dispatcher layered below PCH MSI initialization.

## Important APIs, Types, And Functions
`struct avecintc_chip` stores the lock, fwnode, domain, vector matrix, and MSI base address. `struct avecintc_data` tracks each IRQ's current and previous CPU/vector plus migration state. Important functions are `avecintc_init()`, `avecintc_domain_alloc()`, `avecintc_alloc_vector()`, `avecintc_set_affinity()`, `complete_irq_moving()`, `avecintc_irq_dispatch()`, `avecintc_compose_msi_msg()`, and `avecintc_acpi_init()`.

## Control Flow
ACPI initialization creates a named fwnode and tree domain, maps the AVEC CPU interrupt from the parent CPUINTC, initializes an IRQ matrix with legacy vectors reserved, chains the AVEC dispatcher, registers CPU hotplug callbacks, enables AVEC in IOCSR, then parses the MSI PIC MADT entry to set the MSI base and initialize PCH MSI over the AVEC domain. Allocation reserves a vector on an online CPU, stores the descriptor in per-CPU `irq_map`, and installs an edge IRQ. Dispatch repeatedly reads CSR IRR until invalid and handles the descriptor mapped to each vector.

## State And Persistence
Per-IRQ allocation state persists in `avecintc_data`; per-CPU vector-to-desc state persists in `irq_map`. SMP migration keeps old vector state in per-CPU pending lists until `complete_irq_moving()` observes that the old ISR bit has cleared, then frees the old vector in the matrix.

## Dependencies And Integration Points
It depends on LoongArch CSRs/IOCSR, IRQ matrix allocation, cpuhotplug, SMP IPI callbacks for `ACTION_CLEAR_VECTOR`, MSI library domain selection, ACPI MADT MSI PIC parsing, and `pch_msi_acpi_init_avec()`. It is invoked from the LoongArch CPU interrupt controller when `cpu_has_avecint` is true.

## Risks
Vector migration is subtle: freeing the old vector before hardware clears it can misdeliver interrupts. The global `intersect_mask` is protected by the AVEC lock and must not be used locklessly. MSI message composition packs CPU and vector into an address, so bit masks and `AVEC_MSG_OFFSET` must match hardware.

## Test Signals
Test MSI allocation/free, vector exhaustion, interrupt delivery on all online CPUs, affinity changes during load, CPU hotplug online/offline, `complete_irq_moving()` IPI flow, PCH MSI initialization through ACPI, and unexpected-vector warning paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongarch-avec.c -->
