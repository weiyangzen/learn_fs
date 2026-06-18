<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.c

## Purpose
`omap-wakeupgen.c` implements the OMAP WakeupGen interrupt-controller extension layered above the ARM GIC. It manages wakeup-enable bits for shared peripheral interrupts, interrupt domain allocation, hotplug masking, CPU cluster PM context save/restore, and secure save paths.

## Important APIs, Types, and Functions
Public functions are `omap_get_wakeupgen_base()` and `omap_secure_apis_support()`. Major internals include `struct omap_wakeupgen_ops`, `wakeupgen_mask()`, `wakeupgen_unmask()`, `wakeupgen_irq_set_type()`, hotplug mask helpers, OMAP4/OMAP5/AM43xx context save/restore functions, `irq_notifier()`, `wakeupgen_chip`, `wakeupgen_domain_translate()`, `wakeupgen_domain_alloc()`, and `wakeupgen_init()`.

## Control Flow
`IRQCHIP_DECLARE` calls `wakeupgen_init()` from DT. It resolves the parent GIC domain, maps WakeupGen registers, selects bank/IRQ counts and context ops by SoC, creates a hierarchical IRQ domain, masks all wakeupgen banks, initializes IRQ target CPU bookkeeping, enables OMAP5/DRA7 ES2 PM mode through SMC, registers hotplug and CPU PM notifiers, and records SAR base. Mask/unmask updates WakeupGen enable bits under a raw spinlock before delegating to the parent GIC chip. CPU cluster PM save writes WakeupGen/AuxCoreBoot/PTMSYNC state to SAR or uses secure dispatcher on HS devices.

## State and Persistence Behavior
State includes `wakeupgen_base`, `sar_base`, `irq_target_cpu[]`, bank/IRQ counts, secure API flag, per-CPU hotplug mask snapshots, and optional CPU PM context arrays. SAR RAM preserves wakeupgen state across MPUSS low-power states; AM43xx restores from in-RAM `wakeupgen_context`.

## Dependencies and Integration Points
It depends on irqchip/irqdomain hierarchy, OF address mapping, CPU hotplug, CPU PM notifiers, OMAP secure APIs, SAR layout, SoC/erratum detection, and GIC parent domains. It integrates with SMP, MPUSS low-power, `omap-smp.c`, and DT compatible `ti,omap4-wugen-mpu`.

## Risks
WakeupGen and GIC masks must remain synchronized or interrupts can be lost. IRQ type inversion for `sys_nirq` can surprise board DTS authors. Wrong bank counts or SAR offsets break wake from deep idle. Secure-vs-GP save path mistakes can fail HS resume. Affinity is tracked simplistically and notes missing full support.

## Test Signals
Boot with WakeupGen DT node and parent GIC, allocate SPIs through the hierarchical domain, test GPIO/peripheral wake from idle, CPU hotplug, MPUSS OSWR, and suspend/resume on GP and HS devices. Watch for lost interrupts, polarity warnings, and SAR backup status behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap-wakeupgen.c -->
