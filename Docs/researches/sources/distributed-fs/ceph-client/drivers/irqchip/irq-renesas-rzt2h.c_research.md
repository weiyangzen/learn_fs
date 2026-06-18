<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzt2h.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzt2h.c

## Purpose
`irq-renesas-rzt2h.c` implements the Renesas RZ/T2H ICU hierarchical interrupt controller. It routes non-safety, safety, external IRQ, and SEI inputs to a parent domain and also exports a helper for DMAC request selection.

## Important APIs, Types, and Functions
`struct rzt2h_icu_priv` holds non-safety and safety MMIO bases, parent fwspecs, and a lock. Public API `rzt2h_icu_register_dma_req()` writes DMAC request-selection fields and is exported GPL. IRQ helpers include `rzt2h_icu_irq_to_offset()`, `rzt2h_icu_irq_set_type()`, `rzt2h_icu_set_type()`, `rzt2h_icu_alloc()`, and `rzt2h_icu_parse_interrupts()`.

## Control Flow
Probe finds the parent domain, allocates private state, maps two register banks, parses parent interrupts for all local hwirqs, enables runtime PM, and creates a hierarchical domain. Allocation translates a two-cell child spec, installs `rzt2h_icu_chip`, and forwards allocation to the pre-parsed parent fwspec. Set-type only allows selectable modes for IRQ_NS, IRQ_S, and SEI; internal CPU interrupts are restricted to rising edge and delegated to the parent.

## State and Persistence
Software state is per platform device. The lock serializes trigger mode and DMAC selection register updates. Hardware register state is volatile; there is no syscore or runtime PM register cache in this driver.

## Dependencies and Integration Points
The file depends on the public Renesas RZ/T2H irqchip header, platform driver irqchip macros, reset/runtime PM, parent irqdomains, and DMAC clients that call the exported request-registration helper.

## Risks and Edge Cases
The hwirq layout is encoded by compile-time ranges; DT interrupt ordering must exactly match `RZT2H_ICU_NUM_IRQ`. Safety and SEI sources use the safety register space and a shifted offset; mistakes route writes to the wrong bank. DMAC helper trusts the supplied platform device and channel indexes.

## Test Signals
Exercise all hwirq ranges, type rejection for non-selectable internal CPU interrupts, low/falling/rising/both mode programming for external/SEI lines, parent fwspec forwarding, PM runtime activation, and DMAC request selection writes for multiple channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-renesas-rzt2h.c -->
