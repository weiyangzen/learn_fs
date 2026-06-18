# sources/distributed-fs/ceph-client/drivers/cache/sifive_ccache.c

## Purpose
`sifive_ccache.c` supports SiFive-compatible composable cache controllers, including ECC interrupt reporting, cacheinfo private attributes, optional debugfs ECC injection, and nonstandard cache flush operations for some RISC-V SoCs.

## Important APIs, Types, And Functions
Global state includes `ccache_base`, ECC IRQ numbers, cacheinfo ops, and cache level. `sifive_ccache_init()` maps the controller and registers cacheinfo/nonstandard ops. `sifive_ccache_probe()` requests ECC IRQs. `ccache_int_handler()` handles correctable and uncorrectable directory/data ECC events. `register_sifive_ccache_error_notifier()` and `unregister_sifive_ccache_error_notifier()` export an atomic notifier chain.

## Control Flow
Architecture init finds a matching cache node, maps registers, reads `cache-level`, optionally registers nonstandard cache ops for compatible strings with the quirk, prints configuration, installs cacheinfo private attributes, optionally creates debugfs injection controls, and registers the platform driver. Platform probe counts IRQs and requests each ECC interrupt, skipping broken DATA_UNCORR where marked. Interrupt handling reads address/count registers, clears the interrupt by reading count, notifies listeners, and panics on directory uncorrectable errors while only logging/notifying data uncorrectable errors.

## State And Persistence
The driver uses singleton global state for the mapped controller and cache level. ECC counts persist in hardware registers until read. `number_of_ways_enabled` exposes live WAYENABLE state via sysfs cacheinfo private attributes. Debugfs can persist as long as the driver is loaded.

## Dependencies And Integration Points
It depends on OF compatible data, platform IRQs, RISC-V cacheinfo hooks, optional `CONFIG_RISCV_NONSTANDARD_CACHE_OPS`, optional debugfs, and the exported SiFive cache error notifier API used by other kernel consumers.

## Risks And Edge Cases
The singleton design assumes one relevant cache controller. Nonstandard flush writes one line at a time with memory barriers before and after; large ranges can be expensive. IRQ array indexing assumes the hardware IRQ order matches the enum. The DATA_UNCORR quirk hides one broken interrupt. Directory uncorrectable ECC intentionally panics, so false IRQ mapping is severe. Debugfs injection validates only numeric ranges, not platform safety.

## Test Signals
Boot with each compatible string, verify cacheinfo `number_of_ways_enabled`, trigger correctable and uncorrectable ECC paths where safe, test notifier registration/unregistration, exercise nonstandard flush on DMA workloads, and validate debugfs injection only under debug builds.
