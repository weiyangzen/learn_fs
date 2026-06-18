# sources/distributed-fs/ceph-client/kernel/irq/ipi-mux.c

## Purpose
`ipi-mux.c` multiplexes several virtual IPIs over one physical parent IPI. It creates an IPI irq_domain whose virtual IRQs set per-CPU pending bits and use a caller-provided callback to trigger the actual hardware IPI.

## Important APIs, types, and functions
The central type is per-CPU `struct ipi_mux_cpu` with atomic `enable` and `bits` masks. Public APIs are `ipi_mux_create()` and `ipi_mux_process()`. Internal chip callbacks are `ipi_mux_mask()`, `ipi_mux_unmask()`, and `ipi_mux_send_mask()`, installed in `ipi_mux_chip`. Domain allocation uses `ipi_mux_domain_alloc()` and `ipi_mux_domain_ops`.

## Control flow
`ipi_mux_create()` allocates per-CPU state, creates a named fwnode and linear IPI domain, marks it as single-HW-IPI, allocates virtual IRQs, and stores the send callback. Sending a virtual IPI sets the target CPU's pending bit with release semantics, then sends the physical IPI if the bit was newly pending and enabled. Unmasking enables the local bit and sends a self IPI if work was already pending. The parent physical IPI handler calls `ipi_mux_process()`, which atomically clears enabled pending bits and dispatches each set hwirq through `generic_handle_domain_irq()`.

## State and persistence
State persists globally after creation: `ipi_mux_pcpu`, `ipi_mux_domain`, and `ipi_mux_send`. Each CPU maintains enabled and pending virtual IPI masks atomically. There is no teardown path in this file and no disk persistence.

## Dependencies and integration points
This file depends on SMP, IRQ domains, per-CPU allocation, atomic ordering, generic per-CPU devid IRQ handling, and architecture/irqchip parent IPI code that calls `ipi_mux_process()` when the physical interrupt arrives. It exposes virtual IPIs through the standard generic IPI domain API.

## Risks and test signals
Risks include missing teardown support, `nr_ipi` limited by `int` bit width, memory-ordering bugs that lose IPIs around mask/unmask, duplicate creation returning `-EEXIST`, and parent handlers failing to call `ipi_mux_process()`. Test signals include sending masked then unmasking, multiple virtual IPIs to one CPU, multi-CPU masks, duplicate create failure, invalid `nr_ipi`/callback rejection, and stress tests around concurrent send/unmask.
