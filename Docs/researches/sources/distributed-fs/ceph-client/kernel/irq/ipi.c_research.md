# sources/distributed-fs/ceph-client/kernel/irq/ipi.c

## Purpose
`ipi.c` implements generic APIs for reserving, destroying, querying, and sending inter-processor interrupts through IRQ domains. It abstracts both single-HW-IRQ IPI domains and per-CPU-HW-IRQ domains.

## Important APIs, types, and functions
Public functions are `irq_reserve_ipi()`, `irq_destroy_ipi()`, `ipi_get_hwirq()`, `ipi_send_single()`, and `ipi_send_mask()`. Internal fast paths are `__ipi_send_single()`, `__ipi_send_mask()`, and verification helper `ipi_send_verify()`. The code uses `irq_domain_is_ipi*()` helpers, `__irq_domain_alloc_irqs()`, `irq_domain_free_irqs()`, descriptor allocation/free, irqdata affinity masks, and chip `ipi_send_single`/`ipi_send_mask` callbacks.

## Control flow
Reservation validates the domain and destination mask, computes the number of Linux IRQs needed, requires consecutive CPU masks for per-CPU domains, allocates descriptors, allocates domain IRQs, copies destination affinity into each irqdata, stores the per-CPU offset, and marks IRQs no-balancing. Destroy validates that the target is an IPI and that the requested destroy mask is a subset of the reservation, then frees one or many virqs depending on domain type. Send APIs validate chip callbacks and destination subset, then either call a mask send callback or iterate CPUs calling single-send with adjusted per-CPU irqdata.

## State and persistence
IPI reservation state persists in allocated descriptors, irqdomain mappings, irqdata affinity masks, and `ipi_offset`. It lasts until `irq_destroy_ipi()` or domain teardown. No state is persistent outside the running kernel.

## Dependencies and integration points
The file integrates SMP core code, architecture irqchip IPI drivers, IRQ domains, descriptor allocation, and generic chip send callbacks. It is selected by `GENERIC_IRQ_IPI` and assumes domain flags correctly identify IPI type and bus token behavior.

## Risks and test signals
Risks include accepting non-consecutive per-CPU masks, failing to unwind descriptor/domain allocation, invalid subset checks on destroy/send, using wrong irqdata for per-CPU domains, and chip implementations missing required send callbacks. Test signals include single and per-CPU IPI domains, masks with holes, empty and impossible destination masks, reserve/destroy subset behavior, `ipi_get_hwirq()` for valid and invalid CPUs, and send-single/send-mask fallback paths.
