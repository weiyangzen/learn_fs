# sources/distributed-fs/ceph-client/arch/powerpc/platforms/512x/mpc5121_ads_cpld.c

## Purpose
`mpc5121_ads_cpld.c` implements the ADS board cascaded CPLD interrupt controller. The CPLD exposes PCI and miscellaneous interrupt status/mask registers behind one upstream interrupt.

## Important APIs, Types, and Functions
`mpc5121_ads_cpld_map()` locates and maps `"fsl,mpc5121ads-cpld-pic"`. `mpc5121_ads_cpld_pic_init()` configures routing/masks, creates a 16-entry linear irq domain, and attaches `cpld_pic_cascade()` as the chained handler. The `cpld_pic` irq chip masks, unmasks, and acks by modifying PCI or misc mask bytes. `cpld_pic_get_irq()` picks the first unmasked active-low status bit after ignore masks.

## Control Flow, State, and Persistence
Persistent state consists of `cpld_regs`, `cpld_pic_node`, and `cpld_pic_host`. Interrupt handling first checks PCI status bits, then misc status bits, and dispatches the first pending hwirq to the domain.

## Dependencies and Integration Points
It depends on OF address/IRQ parsing, generic irq domains, chained irq handlers, and the ADS board file. Touchscreen pendown is explicitly ignored because it is routed directly to IPIC IRQ1.

## Risks and Test Signals
Risks include active-low bit assumptions, only servicing one pending CPLD interrupt per cascade entry, missing cleanup for permanent init-time mappings, and route/mask values tied to board wiring. Test signals include PCI slot IRQs, miscellaneous CPLD IRQs, touchscreen direct IRQ behavior, and logs for missing node, failed cascade mapping, or failed irq-domain allocation.
