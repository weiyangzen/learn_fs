<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htpic.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htpic.c

### Purpose
`irq-loongson-htpic.c` initializes the Loongson HyperTransport PIC bridge used to feed legacy i8259-style interrupts into the Linux IRQ subsystem. It owns one global HTPIC instance, maps the controller registers, builds the i8259 IRQ domain, and cascades up to four parent interrupt lines into that domain.

### Important APIs, Types, And Functions
The key state is `struct loongson_htpic`, carrying the MMIO base and i8259-backed `irq_domain`. `htpic_of_init()` is the OF entry declared by `IRQCHIP_DECLARE()`. `htpic_irq_dispatch()` is the chained parent handler, and `htpic_reg_init()` resets cause/enable registers. `htpic_syscore_ops` restores register state on resume by re-running initialization.

### Control Flow
During boot, the OF initializer rejects duplicate controllers, maps MMIO, calls `__init_i8259_irqs(node)`, parses parent IRQs with `irq_of_parse_and_map()`, initializes all eight HT vector enable/cause slots, enables the low 16 vectors, and installs `htpic_irq_dispatch()` on each parent. Dispatch reads the first cause register, writes the same value back to acknowledge all currently pending bits, reports spurious entries when no valid bit exists, and calls `generic_handle_domain_irq()` for bits 0-15.

### State, Persistence, And Dependencies
Persistent state is the singleton `htpic`, the i8259 domain, parent chained handlers, and syscore registration. It depends on OF address/IRQ parsing, i8259 initialization, chained IRQ helpers, raw MMIO access, and syscore resume ordering.

### Integration Points
This driver is the legacy PIC endpoint in Loongson HT systems. It bridges firmware-described HT parent interrupts to the i8259 IRQ domain consumed by legacy ISA-style devices.

### Risks
Only one HTPIC is supported. Dispatch intentionally acknowledges all pending bits before walking them, which avoids flood behavior but relies on hardware latch semantics. Bits above 15 are treated as spurious even though the register is 32-bit. Failure paths remove the IRQ domain and unmap MMIO, but successful init has no remove path.

### Test Signals
Boot with valid and missing parent IRQs, verify legacy IRQ0-15 delivery, trigger simultaneous pending bits, suspend/resume with enabled devices, and check spurious accounting when parent IRQ fires with an empty cause register.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-htpic.c -->
