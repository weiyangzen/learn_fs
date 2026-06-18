<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/irq-common.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-imx/irq-common.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-imx/irq-common.c` belongs to NXP/Freescale i.MX ARM machine support in the Ceph-client kernel source snapshot. It implements interrupt-controller or interrupt-domain glue around memory-mapped platform registers.

### Important APIs, Types, And Functions
Notable functions/entry points: `mxc_set_irq_fiq`. Types: structs `irq_chip_generic`, `mxc_extra_irq`, `irq_data`, enums none.

### Control Flow
Runtime flow follows the local helper sequence around `mxc_set_irq_fiq`; init functions set up register mappings before later callbacks touch hardware.

### State, Persistence, And Dependencies
Dependencies include `linux/module.h`, `linux/irq.h`, `linux/platform_data/asoc-imx-ssi.h`, `irq-common.h`. Local/static state or exported register data includes `struct irq_chip_generic *gc`, `struct mxc_extra_irq *exirq`, `int ret`, `struct irq_data *d = irq_get_irq_data(irq)`. Compatible strings or firmware/device-tree identifiers observed: none. State is kernel-resident and hardware-backed: MMIO registers, interrupt masks, reset vectors, wakeup masks, clock/regulator settings, and cached CPU revision variables survive only as long as the running kernel unless the underlying PMU/SRAM/firmware register preserves them across suspend.

### Integration Points
Integration points are adjacent platform C/assembly files through shared macros, prototypes, or build rules. Callers should treat `mxc_set_irq_fiq` as platform hooks rather than generic APIs when those symbols are visible.

### Risks
Primary risks include interrupt masking/wakeup regressions.

### Test Signals
Useful test signals include ARM build coverage for the relevant CONFIG symbols, interrupt storm, mask/unmask, and wake-capable IRQ tests. Source reading signal: 31 lines; 4 includes; 1 function/entry point; 0 macro/defines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/irq-common.c -->
