<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-liointc.c -->
## sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-liointc.c

### Purpose
`irq-loongson-liointc.c` implements the Loongson local I/O interrupt controller with 32 child interrupts, four parent lines, and per-core status registers. It supports OF revisions 1.0/1.0a/2.0 and ACPI MADT initialization, then cascades to HT vector controllers when present.

### Important APIs, Types, And Functions
`struct liointc_priv` holds the generic chip, parent handler data, core ISR addresses, route-map cache, saved polarity/edge registers, and errata flag. `liointc_init()` is shared initialization. `liointc_chained_handle_irq()` handles parent IRQs. `liointc_set_type()` programs edge/polarity bits. `liointc_suspend()` and `liointc_resume()` preserve programmable state. `liointc_acpi_init()` is the ACPI entry.

### Control Flow
Firmware supplies parent IRQs and `loongson,parent_int_map` masks. Initialization maps registers, optionally remaps per-core ISR regions for revision 2, creates a linear domain using generic-chip ops or ACPI xlate ops, allocates one generic chip, disables all interrupts, defaults to level mode, builds route bytes from parent maps plus boot CPU routing, writes the route table, configures generic-chip enable/disable/type callbacks, and chains each parent IRQ. Dispatch reads the current core's status register and handles each pending child bit.

### State, Persistence, And Dependencies
Persistent state is the linear domain, generic-chip mask cache, route table cache, saved edge/polarity values, parent maps, and global `liointc_handle`. It depends on Loongson CPU/core ID helpers, boot CPU ID configuration, generic IRQ chips, OF or ACPI firmware data, and HTVEC ACPI cascade creation.

### Integration Points
The domain sits below CPU/parent interrupt controllers and above HTVEC/PCH domains on ACPI systems. Child IRQ consumers use normal firmware IRQ specifiers, while ACPI specs are translated from GSI space using `GSI_MIN_CPU_IRQ`.

### Risks
Parent maps are global static arrays and must be fully populated before init. Revision-2 per-core ISR remapping can leave mixed base-derived and separately mapped ISR pointers. The LPC errata path fabricates IRQ10 pending when hardware reports none, so false positives are possible but intentional. Resume restores route and mask state under the generic-chip lock.

### Test Signals
Exercise all supported compatibles, parent map parsing, IRQ type changes, per-core delivery, LPC errata behavior, ACPI HT_PIC cascade parsing, suspend/resume register restoration, and invalid firmware maps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/irqchip/irq-loongson-liointc.c -->
