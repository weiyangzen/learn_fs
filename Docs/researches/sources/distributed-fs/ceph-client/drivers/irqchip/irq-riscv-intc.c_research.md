<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-intc.c

## Purpose
`irq-riscv-intc.c` implements the per-hart RISC-V local interrupt controller. It is the root domain for local interrupt causes and the parent for PLIC, CLINT/SBI IPI, APLIC direct, IMSIC, and other local-interrupt consumers.

## Important APIs, Types, and Functions
Root handlers are `riscv_intc_irq()` for classic cause-based delivery and `riscv_intc_aia_irq()` for AIA TOPI delivery. Chip callbacks are standard CSR mask/unmask, Andes-specific `SLIE` mask/unmask, and dummy EOI. Domain operations are map, alloc, xlate, and free. Common initialization is `riscv_intc_init_common()`. DT init is `riscv_intc_init()`, with ACPI RINTC parsing helpers under `CONFIG_ACPI`.

## Control Flow
DT contains one INTC node per hart; only the boot CPU's node creates the irqdomain, while other nodes are marked initialized for supplier dependency purposes. Common init creates a tree domain, selects AIA or classic root handler based on ISA extension, registers the global RISC-V INTC fwnode callback, and logs mapped interrupt counts. Allocation maps one-cell hwirqs only if they are within standard or configured custom ranges, marks IRQs percpu-devid, and uses `handle_percpu_devid_irq`.

## State and Persistence
Global state is the root domain, standard IRQ count, custom interrupt base/count, and ACPI RINTC table cache. Mask state lives in local hart CSRs (`IE`, `IEH`, or Andes `SLIE`) and is not persistent across CPU reset.

## Dependencies and Integration Points
It depends on RISC-V CSR access, ISA extension detection, SMP hart ID mapping, OF/ACPI MADT RINTC data, irqdomain tree domains, and child irqchip discovery through `riscv_set_intc_hwnode_fn()`.

## Risks and Edge Cases
CSR mask/unmask can only operate on the local hart. AIA raises the local IRQ count to 64 and uses `TOPI` claim loops. Andes custom local interrupts use hwirq causes starting at 256. ACPI helpers cache per-RINTC data for PLIC/APLIC/IMSIC lookup.

## Test Signals
Validate boot CPU domain creation, non-boot node supplier marking, classic and AIA root handlers, local timer/software/external interrupts, Andes custom SLI interrupts, ACPI RINTC parsing helpers, and rejection of out-of-range hwirqs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-riscv-intc.c -->
