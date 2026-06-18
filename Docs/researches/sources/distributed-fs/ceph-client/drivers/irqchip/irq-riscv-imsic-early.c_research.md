<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-early.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-early.c

## Purpose
`irq-riscv-imsic-early.c` performs early RISC-V IMSIC setup for interrupt delivery and IPIs before the platform MSI domain is created.

## Important APIs, Types, and Functions
Global state is `imsic_parent_irq` and boot parameter `imsic_noipi`. IPI helpers are `imsic_ipi_send()`, CPU start/stop IPI hooks, and `imsic_ipi_domain_init()`. Runtime delivery uses `imsic_handle_irq()`, `imsic_hw_states_init()`, CPU hotplug callbacks, CPU PM notifier, `imsic_early_probe()`, DT init `imsic_early_dt_init()`, and ACPI init `imsic_early_acpi_init()`.

## Control Flow
Early DT/ACPI init calls `imsic_setup_state()` to parse firmware and allocate global/per-CPU state. It then maps the RISC-V INTC external interrupt, optionally creates an IPI mux using IMSIC ID 1, installs the chained IMSIC handler, registers CPU hotplug callbacks, and registers a CPU PM notifier. The handler syncs pending local vector updates, repeatedly swaps `CSR_TOPEI` to claim IDs, processes IPI IDs via the IPI mux, and dispatches non-IPI vectors through per-CPU vector state.

## State and Persistence
This file controls local IMSIC delivery state and IPI enablement. CPU online and CPU PM exit paths re-enable IPI ID, synchronize all local IDs, and enable IMSIC local delivery. ACPI stores a global IMSIC fwnode for later MSI-domain setup.

## Dependencies and Integration Points
It depends on `irq-riscv-imsic-state.c`, RISC-V INTC root domain, CPU hotplug, CPU PM, IPI mux, PCI MSI fwnode provider registration under ACPI, and AIA CSRs.

## Risks and Edge Cases
Boot parameter `irqchip.riscv_imsic_noipi` disables IMSIC IPI provision. Even if ACPI MSI platform setup fails, IPI delivery continues. The handler assumes vector state exists for claimed IDs; out-of-range IDs are rate-limited warnings.

## Test Signals
Validate early DT and ACPI boot, IPI send/receive, `noipi` boot parameter, CPU hotplug, CPU PM resume, chained external interrupt handling, invalid local ID warnings, and coexistence with later platform MSI-domain probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-imsic-early.c -->
