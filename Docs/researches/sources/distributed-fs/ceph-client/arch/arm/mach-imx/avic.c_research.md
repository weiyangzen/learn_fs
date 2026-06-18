<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/avic.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-imx/avic.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-imx/avic.c` belongs to NXP/Freescale i.MX ARM machine support in the Ceph-client kernel source snapshot. It implements interrupt-controller or interrupt-domain glue around memory-mapped platform registers.

### Important APIs, Types, And Functions
Notable functions/entry points: `avic_set_irq_fiq`, `avic_irq_suspend`, `avic_irq_resume`, `avic_init_gc`, `avic_handle_irq`, `mxc_init_irq`, `imx_avic_init`. Types: structs `irq_chip_generic`, `irq_chip_type`, `device_node`, enums none. Important macros/register names include `AVIC_INTCNTL`, `AVIC_NIMASK`, `AVIC_INTENNUM`, `AVIC_INTDISNUM`, `AVIC_INTENABLEH`, `AVIC_INTENABLEL`, `AVIC_INTTYPEH`, `AVIC_INTTYPEL`, `AVIC_NIPRIORITY(x)`, `AVIC_NIVECSR`, `AVIC_FIVECSR`, `AVIC_INTSRCH`, `AVIC_INTSRCL`, `AVIC_INTFRCH`, `AVIC_INTFRCL`, `AVIC_NIPNDH`, `AVIC_NIPNDL`, `AVIC_FIPNDH`, `AVIC_FIPNDL`, `AVIC_NUM_IRQS`, `MX25_CCM_LPIMR0`, `MX25_CCM_LPIMR1`, `avic_irq_suspend`, `avic_irq_resume`. Registration macros/init hooks: `imx_avic, "fsl,avic", imx_avic_init`.

### Control Flow
IRQ initialization maps MMIO, creates an irq domain/chip, translates firmware specs, then forwards mask/unmask/eoi/type operations to parent domains where applicable. Suspend paths save selected registers, mask non-wakeup IRQs, enter firmware or CPU suspend callbacks, then restore register state and wake masks during resume.

### State, Persistence, And Dependencies
Dependencies include `linux/module.h`, `linux/irq.h`, `linux/irqdomain.h`, `linux/irqchip.h`, `linux/io.h`, `linux/of.h`, `linux/of_address.h`, `asm/mach/irq.h`, `asm/exception.h`, `common.h`, `hardware.h`, `irq-common.h`. Local/static state or exported register data includes `static void __iomem *avic_base`, `static void __iomem *mx25_ccm_base`, `static struct irq_domain *domain`, `unsigned int irqt`, `static struct mxc_extra_irq avic_extra_irq = {`, `static u32 avic_saved_mask_reg[2]`, `struct irq_chip_generic *gc = irq_data_get_irq_chip_data(d)`, `struct irq_chip_type *ct = gc->chip_types`, `int idx = d->hwirq >> 5`, `struct irq_chip_generic *gc`, `struct irq_chip_type *ct`, `u32 nivector`, and 5 more. Compatible strings or firmware/device-tree identifiers observed: `fsl,imx25-ccm`, `fsl,avic`. State is kernel-resident and hardware-backed: MMIO registers, interrupt masks, reset vectors, wakeup masks, clock/regulator settings, and cached CPU revision variables survive only as long as the running kernel unless the underlying PMU/SRAM/firmware register preserves them across suspend.

### Integration Points
Integration points are Linux irqchip/irqdomain hierarchy, PM core, syscore, and CPU suspend/resume, legacy platform devices such as LED, RTC, timer, and ISA DMA. Callers should treat `avic_set_irq_fiq`, `avic_irq_suspend`, `avic_irq_resume`, `avic_init_gc`, `avic_handle_irq`, `mxc_init_irq`, `imx_avic_init` as platform hooks rather than generic APIs when those symbols are visible.

### Risks
Primary risks include MMIO or port-I/O ordering, missing barriers, and incorrect register bit definitions, interrupt masking/wakeup regressions, resume failures, lost wakeups, and low-power state mismatches, missing devicetree nodes or leaked mappings/references on error paths.

### Test Signals
Useful test signals include ARM build coverage for the relevant CONFIG symbols, devicetree boot logs showing compatible match and platform device population, interrupt storm, mask/unmask, and wake-capable IRQ tests, suspend-to-RAM, idle entry/exit, and wake-source validation, GPIO/LED state readback on target hardware. Source reading signal: 236 lines; 12 includes; 7 function/entry points; 24 macro/defines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/avic.c -->
