<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/isa-irq.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/isa-irq.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/isa-irq.c` belongs to Intel/DEC Footbridge ARM platform support in the Ceph-client kernel source snapshot. It implements interrupt-controller or interrupt-domain glue around memory-mapped platform registers.

### Important APIs, Types, And Functions
Notable functions/entry points: `isa_mask_pic_lo_irq`, `isa_ack_pic_lo_irq`, `isa_unmask_pic_lo_irq`, `isa_mask_pic_hi_irq`, `isa_ack_pic_hi_irq`, `isa_unmask_pic_hi_irq`, `isa_irq_handler`, `isa_init_irq`.

### Control Flow
Runtime flow follows the local helper sequence around `isa_mask_pic_lo_irq`, `isa_ack_pic_lo_irq`, `isa_unmask_pic_lo_irq`, `isa_mask_pic_hi_irq`, `isa_ack_pic_hi_irq`, `isa_unmask_pic_hi_irq`, `isa_irq_handler`, `isa_init_irq`; init functions set up register mappings before later callbacks touch hardware.

### State, Persistence, And Dependencies
Dependencies include `linux/ioport.h`, `linux/interrupt.h`, `linux/list.h`, `linux/init.h`, `linux/io.h`, `linux/spinlock.h`, `asm/mach/irq.h`, `mach/hardware.h`, `asm/hardware/dec21285.h`, `asm/irq.h`, `asm/mach-types.h`, `common.h`. Local/static state or exported register data includes `unsigned int mask = 1 << (d->irq & 7)`, `static struct irq_chip isa_lo_chip = {`, `static struct irq_chip isa_hi_chip = {`, `unsigned int isa_irq = *(unsigned char *)PCIIACK_BASE`, `static struct resource pic1_resource = {`, `static struct resource pic2_resource = {`, `unsigned int irq`. Compatible strings or firmware/device-tree identifiers observed: none. State is kernel-resident and hardware-backed: MMIO registers, interrupt masks, reset vectors, wakeup masks, clock/regulator settings, and cached CPU revision variables survive only as long as the running kernel unless the underlying PMU/SRAM/firmware register preserves them across suspend.

### Integration Points
Integration points are PCI host/fixup code, legacy platform devices such as LED, RTC, timer, and ISA DMA. Callers should treat `isa_mask_pic_lo_irq`, `isa_ack_pic_lo_irq`, `isa_unmask_pic_lo_irq`, `isa_mask_pic_hi_irq`, `isa_ack_pic_hi_irq`, `isa_unmask_pic_hi_irq`, `isa_irq_handler`, `isa_init_irq` as platform hooks rather than generic APIs when those symbols are visible.

### Risks
Primary risks include MMIO or port-I/O ordering, missing barriers, and incorrect register bit definitions, interrupt masking/wakeup regressions.

### Test Signals
Useful test signals include ARM build coverage for the relevant CONFIG symbols, interrupt storm, mask/unmask, and wake-capable IRQ tests, PCI enumeration and board-specific fixup checks, GPIO/LED state readback on target hardware. Source reading signal: 177 lines; 12 includes; 8 function/entry points; 0 macro/defines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-footbridge/isa-irq.c -->
