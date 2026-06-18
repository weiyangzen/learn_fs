<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-pruss-intc.c -->
# sources/distributed-fs/ceph-client/drivers/irqchip/irq-pruss-intc.c

## Purpose
`irq-pruss-intc.c` is the TI PRU-ICSS/ICSSG interrupt controller driver. It maps PRU system events to PRU channels and host interrupts, then demultiplexes host interrupt lines presented to the MPU.

## Important APIs, Types, and Functions
`struct pruss_intc` owns event-to-channel and channel-to-host reference-counted maps, host IRQs, MMIO base, domain, SoC limits, device pointer, and a mutex. `struct pruss_intc_map_record` tracks a mapped value and refcount. Hardware helpers update CMR/HMR registers. Mapping lifecycle is `pruss_intc_validate_mapping()`, `pruss_intc_map()`, and `pruss_intc_unmap()`. IRQ callbacks include ACK/mask/unmask, request/release resources, pending get/set state, domain xlate/map/unmap, and the chained `pruss_intc_irq_handler()`.

## Control Flow
Probe reads SoC match data, maps registers, optionally reads `ti,irqs-reserved`, initializes all system events as active-high level, clears CMR/HMR, enables global interrupts, creates a linear domain, and attaches chained handlers for available host interrupt resources. DT interrupt cells specify system event, channel, and host. Translation validates ranges and conflicting mappings. Mapping writes CMR/ESR/SECR, enables the host mapping on first channel user, and installs a level IRQ chip. The chained handler repeatedly reads `HIPIR(host)` for the highest-priority pending system event and dispatches the domain IRQ, ACKing unmapped events defensively.

## State and Persistence
The driver maintains non-persistent runtime allocation state in the event/channel refcount arrays. Module references are held while child IRQ resources are requested. Hardware mappings are undone when IRQs are unmapped and fully cleared on driver initialization.

## Dependencies and Integration Points
It is a platform driver for `ti,pruss-intc` and `ti,icssg-intc`, depends on OF IRQ resources named `host_intr0` through `host_intr7`, chained IRQ helpers, irqdomain, and PRU firmware/client DT mappings.

## Risks and Edge Cases
Conflicting reuse of a system event or channel returns `-EBUSY`. The host numbering exposed to hardware is offset by `FIRST_PRU_HOST_INT`; DT cells and named platform IRQs must agree. Reserved host IRQ bits skip platform IRQ acquisition. Unmapped pending events are manually cleared to avoid interrupt storms.

## Test Signals
Exercise multiple clients sharing a mapping, conflict rejection, domain unmap refcount teardown, software pending set/clear via irqchip state, all host interrupt names, `ti,irqs-reserved`, and chained dispatch loops under simultaneous PRU system events.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-pruss-intc.c -->
