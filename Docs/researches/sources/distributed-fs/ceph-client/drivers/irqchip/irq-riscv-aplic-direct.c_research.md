<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-direct.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-direct.c

## Purpose
`irq-riscv-aplic-direct.c` implements direct-delivery mode for the RISC-V APLIC interrupt controller. In this mode APLIC interrupt delivery controllers claim wired interrupts directly through per-hart IDC registers behind the RISC-V local external interrupt.

## Important APIs, Types, and Functions
`struct aplic_direct` embeds shared `aplic_priv`, a domain pointer, and a CPU mask for usable IDCs. `struct aplic_idc` stores hart index, IDC register base, and backpointer. Main callbacks include `aplic_direct_set_affinity()`, `aplic_direct_irqdomain_translate()`, `aplic_direct_irqdomain_alloc()`, `aplic_direct_handle_irq()`, `aplic_idc_set_delivery()`, CPU hotplug callbacks, parent parsing, and `aplic_direct_setup()`.

## Control Flow
Setup allocates direct state, calls `aplic_setup_priv()` for common APLIC state, enumerates parent external interrupts to map IDC indexes to Linux CPUs and hart indexes, enables IDC delivery for each usable CPU, optionally rewrites target registers if the boot CPU hart index is not zero, installs a chained handler on the RISC-V INTC external interrupt, registers CPU hotplug hooks, enables global APLIC direct mode, and creates a linear domain. Runtime handling claims pending IDs from the local IDC `CLAIMI` register until zero and dispatches mapped Linux IRQs.

## State and Persistence
Per-CPU `aplic_idcs` hold IDC register pointers and direct context. Target registers store hart index and priority. CPU hotplug toggles the parent percpu IRQ. Common APLIC suspend/resume calls `aplic_direct_restore_states()` to re-enable IDC delivery.

## Dependencies and Integration Points
It depends on `irq-riscv-aplic-main.c` common helpers, RISC-V INTC fwnode discovery, OF or ACPI hart mapping, CPU hotplug, percpu IRQs, irqdomain top-level allocation, and direct AIA CSR/register definitions.

## Risks and Edge Cases
Only parent hwirq `RV_IRQ_EXT` is accepted. If no CPU has a valid IDC, setup fails. `aplic_direct_parent_irq` is global, so multiple direct APLIC instances share one chained parent path. Affinity requires the target CPU to be in the controller's `lmask`.

## Test Signals
Validate IDC enumeration on DT and ACPI, CPU hotplug enable/disable of parent external IRQ, claim-loop dispatch, affinity target register writes, boot CPU nonzero hart index handling, and restore after PM domain/syscore resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-aplic-direct.c -->
