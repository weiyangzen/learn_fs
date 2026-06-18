<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ompic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-ompic.c

### Purpose
`irq-ompic.c` implements the OpenRISC Open Multi-Processor Interrupt Controller, used for inter-processor interrupts on multi-core OpenRISC systems.

### Important APIs, Types, And Functions
Global `ompic_base` maps the controller. Per-CPU `ops` stores pending IPI message bits and `ipi_dummy_dev` backs the percpu IRQ request. `ompic_raise_softirq()` is registered as the SMP cross-call function. `ompic_ipi_handler()` acknowledges the hardware interrupt and dispatches pending IPI messages via `handle_IPI()`. `ompic_of_init()` validates DT and installs the percpu IRQ.

### Control Flow
Initialization rejects duplicate controllers, validates the MMIO resource size against `num_possible_cpus()`, maps registers, parses the shared per-CPU IPI IRQ, marks it percpu devid, requests it with `request_percpu_irq()`, and registers `set_smp_cross_call()`. Raising an IPI sets the message bit in the destination CPU's per-CPU `ops` word, then writes the source CPU control register with generate, destination, and data bits. The handler acknowledges the CPU's control register, atomically drains pending ops with `xchg()`, and calls `handle_IPI()` for each bit.

### State, Persistence, And Dependencies
Persistent state is the MMIO base, per-CPU pending operation bitmaps, requested percpu IRQ, and architecture cross-call hook. Dependencies include OpenRISC SMP support, OF resource/IRQ parsing, big-endian MMIO accessors, and percpu interrupt APIs.

### Integration Points
The driver provides the low-level IPI transport used by OpenRISC SMP. It does not expose child IRQ domains because OMPIC has no device interrupt inputs.

### Risks
Resource size must cover every possible CPU. Atomic `set_bit()` and `xchg()` are relied on for ordering on OpenRISC; other architectures would need explicit barriers. Hardware IRQ data field is unused except for a constant payload. There is no shutdown path after successful early init.

### Test Signals
Validate duplicate-controller rejection, resource-size checks, percpu IRQ request and enablement, cross-CPU IPI delivery to all online CPUs, multiple pending IPI bits, big-endian register writes, and failure cleanup for IRQ parse/request errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-ompic.c -->
