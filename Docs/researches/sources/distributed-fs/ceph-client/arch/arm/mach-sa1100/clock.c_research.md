<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/clock.c -->
## sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/clock.c

### Purpose
Registers SA1100 clocks for the common clock framework.

### Important APIs, Types, And Functions
Defines GPIO27 clock enable/disable ops guarded by `tucr_lock`, MPLL rate recalculation from `PPCR`, and `sa11xx_clk_init()` to register fixed-factor/mux/hw clocks.

### Control Flow
`sa1100_init_irq()` calls `sa11xx_clk_init()` after IRQ/GPIO initialization. Clock consumers can then enable GPIO27-derived clock output or query CPU/MPLL rate.

### State, Persistence, And Dependencies
State includes clock framework registrations and protected `TUCR` hardware bits. Dependencies include CCF, SA1100 register macros, spinlocks, and CPU frequency state.

### Integration Points
Used by SA1100 generic initialization and devices requiring clock lookup.

### Risks
GPIO27 clock configuration shares `TUCR`; missing locking would race with other users. Rate calculation must match hardware PLL encoding.

### Test Signals
Clock registration logs, cpufreq rate reporting, and GPIO27 clock consumer enable/disable validate it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-sa1100/clock.c -->
