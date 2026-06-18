<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-common.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-common.c

## Purpose
`omap4-common.c` provides common OMAP4/5 platform support for DRAM barriers, SRAM low-power code copy, GIC distributor erratum helpers, L2 cache secure register writes, SAR RAM mapping, and GIC/WakeupGen OF initialization.

## Important APIs, Types, and Functions
Public functions include `omap_interconnect_sync()`, `omap_barrier_reserve_memblock()`, `omap_barriers_init()`, `gic_dist_disable()`, `gic_dist_enable()`, `gic_dist_disabled()`, `gic_timer_retrigger()`, `omap4_get_l2cache_base()`, `omap4_l2c310_write_sec()`, `omap_l2_cache_init()`, `omap4_get_sar_ram_base()`, `omap4_sar_ram_init()`, and `omap_gic_of_init()`.

## Control Flow
Memblock reservation sets aside a DRAM barrier page and initialization maps it, flushes it, and stores a pointer used by the custom memory barrier routine. SRAM init copies OMAP4 low-power code into SRAM. GIC erratum helpers directly disable/enable distributor and retrigger a lost local timer if needed. L2 cache secure writes map public L2 registers to secure monitor service IDs. SAR init maps OMAP4/OMAP5 SAR RAM early. GIC OF init locates WakeupGen, maps GIC/TWD bases for OMAP446x erratum, and calls `irqchip_init()`.

## State and Persistence Behavior
State includes mapped barrier memory, `dram_sync`, GIC distributor/TWD bases, L2 cache base, and SAR RAM base. SAR RAM persists low-power context across MPUSS transitions; other mappings persist for kernel lifetime.

## Dependencies and Integration Points
It depends on memblock, ioremap, cache flush APIs, GIC/TWD register definitions, secure APIs, L2X0, OF irqchip, SAR layout/base headers, SRAM helpers, and SoC detection. It integrates with cpuidle/SMP, MPUSS low-power, WakeupGen, and L2 cache drivers.

## Risks
Barrier reservation/mapping errors can break interconnect synchronization. GIC distributor erratum handling can lose interrupts if timer retrigger logic is wrong. Secure L2 write mapping must match ROM API support. Missing WakeupGen DT node is explicitly warned as system-misbehaving.

## Test Signals
Boot OMAP4/5 with OF irqchips, verify WakeupGen/GIC init, run SMP and idle stress, exercise OMAP446x timer erratum path, initialize L2 cache, and enter/exit MPUSS low-power states. Check for missing DT warnings, lost localtimer warnings, and SAR base availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap4-common.c -->
