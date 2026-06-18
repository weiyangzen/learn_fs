# sources/distributed-fs/ceph-client/drivers/irqchip/irq-ti-sci-inta.c

## Purpose
Implements the TI K3 Interrupt Aggregator as an MSI-capable irq domain backed by TI SCI resource management. It allocates virtual interrupts, global events, and event-to-vint mappings on demand and dispatches MSI events from VINT status registers.

## Important APIs, Types, And Functions
`ti_sci_inta_irq_domain` owns the TI SCI handle, VINT/global-event resources, VINT list, mutex, MMIO base, device ID, and unmapped event-source list. `ti_sci_inta_vint_desc` tracks one VINT, parent virq, and up to 64 event descriptors. Resource allocation is deferred to `irq_request_resources()` via `ti_sci_inta_request_resources()`. The MSI layer uses `ti_sci_inta_msi_domain_info` and `ti_sci_inta_msi_set_desc()`.

## Control Flow
Probe gets the parent domain, TI SCI handle, device ID, VINT/global event resource pools, MMIO base, unmapped event sources, creates the IRQ domain, then creates an MSI domain. MSI allocation stores a packed source device/index hwirq. Requesting resources finds or allocates a VINT parent IRQ, allocates a global event, calls TI SCI `set_event_map`, and stores the event descriptor. The chained VINT handler reads masked status and dispatches the hwirq stored in each set bit.

## State And Persistence
State persists in the VINT list, event bitmaps, TI SCI resource allocations, event descriptors, and hardware VINT enable/status registers. Releasing resources frees TI SCI event maps, global events, parent VINT IRQs, and resource pool entries when a VINT becomes empty.

## Dependencies And Integration Points
Depends on TI SCI protocol/resource APIs, `ti_sci_inta_msi`, generic MSI infrastructure, OF interrupt ranges, parent GIC or interrupt-router domains, and compatible `ti,sci-inta`.

## Risks
Resource lifecycle is split between domain allocation and request_resources to avoid deadlock; regressions can leak VINTs or global events. `ti,interrupt-ranges` and unmapped-event-source handling must match firmware. Affinity is unsupported and returns `-EINVAL`. Level MSI handling depends on trigger type selection and ack suppression for high-level events.

## Test Signals
Exercise MSI consumers with rising and level-high MSIs, allocate more than 64 events to force multiple VINTs, release all events to free VINTs, validate unmapped event sources, and test parent paths through both GIC and TI interrupt router. TI SCI set/free event map failures should clean up resources.
