# sources/distributed-fs/ceph-client/drivers/irqchip/irq-gic-common.c

## Purpose
Provides shared helpers for ARM GIC drivers: quirk matching, interrupt trigger configuration, distributor initialization, and CPU-interface private interrupt initialization.

## Important APIs, Types, and Functions
`gic_enable_of_quirks()` and `gic_enable_quirks()` apply workaround tables. `gic_configure_irq()` changes GIC configuration bits with locking. `gic_dist_config()` initializes global SPIs. `gic_cpu_config()` initializes SGI/PPI priority and disabled state.

## Control Flow
Quirk helpers scan sentinel-terminated `struct gic_quirk` arrays and call `init(data)` when OF compatible/property or IIDR mask matches. IRQ configuration locks a global raw spinlock, updates two-bit trigger fields, writes them back, and verifies hardware accepted the new value. Dist/CPU config loops over register groups writing level-trigger defaults, priorities, active-clear, and enable-clear values.

## State and Persistence
Only a file-local raw spinlock is software state. Persistent hardware state is GIC distributor configuration: trigger modes, priorities, active state, and enable bits.

## Dependencies and Integration Points
Depends on ARM GIC register definitions, OF, irqchip users, and common Linux IRQ type flags. Called by GICv2/v3 and platform-specific wrappers.

## Risks and Test Signals
Risks include hardware refusing configuration writes, especially for PPIs/non-secure state, incorrect priority defaults, and quirk init side effects. Test signals are GIC init logs for enabled workarounds, successful set-type operations, and distributor registers reset to disabled/known priority state.
