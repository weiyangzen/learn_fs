<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/gpc.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-imx/gpc.c

### Purpose
`sources/distributed-fs/ceph-client/arch/arm/mach-imx/gpc.c` belongs to NXP/Freescale i.MX ARM machine support in the Ceph-client kernel source snapshot. It implements interrupt-controller or interrupt-domain glue around memory-mapped platform registers.

### Important APIs, Types, And Functions
Notable functions/entry points: `imx_gpc_set_arm_power_up_timing`, `imx_gpc_set_arm_power_down_timing`, `imx_gpc_set_arm_power_in_lpm`, `imx_gpc_set_l2_mem_power_in_lpm`, `imx_gpc_pre_suspend`, `imx_gpc_post_resume`, `imx_gpc_irq_set_wake`, `imx_gpc_mask_all`, `imx_gpc_restore_all`, `imx_gpc_hwirq_unmask`, `imx_gpc_hwirq_mask`, `imx_gpc_irq_unmask`, `imx_gpc_irq_mask`, `imx_gpc_domain_translate`, `imx_gpc_domain_alloc`, `imx_gpc_init`, `imx_gpc_check_dt`. Types: structs `irq_fwspec`, `device_node`, `irq_domain`, enums none. Important macros/register names include `GPC_CNTR`, `GPC_IMR1`, `GPC_PGC_CPU_PDN`, `GPC_PGC_CPU_PUPSCR`, `GPC_PGC_CPU_PDNSCR`, `GPC_PGC_SW2ISO_SHIFT`, `GPC_PGC_SW_SHIFT`, `GPC_CNTR_L2_PGE_SHIFT`, `IMR_NUM`, `GPC_MAX_IRQS`. Registration macros/init hooks: `imx_gpc, "fsl,imx6q-gpc", imx_gpc_init`.

### Control Flow
IRQ initialization maps MMIO, creates an irq domain/chip, translates firmware specs, then forwards mask/unmask/eoi/type operations to parent domains where applicable. Suspend paths save selected registers, mask non-wakeup IRQs, enter firmware or CPU suspend callbacks, then restore register state and wake masks during resume.

### State, Persistence, And Dependencies
Dependencies include `linux/io.h`, `linux/irq.h`, `linux/irqchip.h`, `linux/of.h`, `linux/of_address.h`, `linux/of_irq.h`, `common.h`, `hardware.h`. Local/static state or exported register data includes `static void __iomem *gpc_base`, `static u32 gpc_wake_irqs[IMR_NUM]`, `static u32 gpc_saved_imrs[IMR_NUM]`, `u32 val`, `void __iomem *reg_imr1 = gpc_base + GPC_IMR1`, `int i`, `unsigned int idx = d->hwirq / 32`, `u32 mask`, `void __iomem *reg`, `static struct irq_chip imx_gpc_chip = {`, `struct irq_fwspec *fwspec,`, `unsigned long *hwirq,`, and 9 more. Compatible strings or firmware/device-tree identifiers observed: `fsl,imx6q-gpc`. State is kernel-resident and hardware-backed: MMIO registers, interrupt masks, reset vectors, wakeup masks, clock/regulator settings, and cached CPU revision variables survive only as long as the running kernel unless the underlying PMU/SRAM/firmware register preserves them across suspend.

### Integration Points
Integration points are Linux irqchip/irqdomain hierarchy, PM core, syscore, and CPU suspend/resume. Callers should treat `imx_gpc_set_arm_power_up_timing`, `imx_gpc_set_arm_power_down_timing`, `imx_gpc_set_arm_power_in_lpm`, `imx_gpc_set_l2_mem_power_in_lpm`, `imx_gpc_pre_suspend`, `imx_gpc_post_resume`, `imx_gpc_irq_set_wake`, `imx_gpc_mask_all` as platform hooks rather than generic APIs when those symbols are visible.

### Risks
Primary risks include MMIO or port-I/O ordering, missing barriers, and incorrect register bit definitions, interrupt masking/wakeup regressions, resume failures, lost wakeups, and low-power state mismatches, missing devicetree nodes or leaked mappings/references on error paths.

### Test Signals
Useful test signals include ARM build coverage for the relevant CONFIG symbols, devicetree boot logs showing compatible match and platform device population, interrupt storm, mask/unmask, and wake-capable IRQ tests, suspend-to-RAM, idle entry/exit, and wake-source validation. Source reading signal: 284 lines; 8 includes; 17 function/entry points; 10 macro/defines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-imx/gpc.c -->
