# sources/distributed-fs/ceph-client/drivers/watchdog/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/Makefile` maps watchdog Kconfig symbols to compiled objects. It builds the watchdog core, optional pretimeout infrastructure and governors, and every enabled hardware/software watchdog driver object in an order chosen to favor physical ISA/PCI/USB devices before architecture-specific and software fallbacks. The complete 243-line file was read for this report.

## Important APIs, Types, and Functions

This is kbuild data. Key assignments include `obj-$(CONFIG_WATCHDOG_CORE) += watchdog.o`, `watchdog-objs += watchdog_core.o watchdog_dev.o`, optional core additions for `watchdog_pretimeout.o` and `watchdog_hrtimer_pretimeout.o`, and governor objects `pretimeout_noop.o` and `pretimeout_panic.o`. Relevant object mappings include `acquirewdt.o`, `advantechwdt.o`, `advantech_ec_wdt.o`, `airoha_wdt.o`, `alim1535_wdt.o`, `alim7101_wdt.o`, `apple_wdt.o`, `arm_smc_wdt.o`, `armada_37xx_wdt.o`, `asm9260_wdt.o`, `aspeed_wdt.o`, `at91rm9200_wdt.o`, `at91sam9_wdt.o`, `ath79_wdt.o`, `bcm2835_wdt.o`, `bcm47xx_wdt.o`, `bcm7038_wdt.o`, and `bcm_kona_wdt.o`.

## Control Flow

Kbuild includes objects conditionally based on `CONFIG_*` values from Kconfig. Composite object `watchdog.o` is assembled from core pieces plus optional pretimeout components. The file is organized by hardware/bus or architecture, with comments explaining that ISA/PCI/USB cards are probed first, then architecture-specific watchdogs, then the software watchdog fallback.

## State and Persistence Behavior

No runtime state is owned. The Makefile determines which object files become built-in or modules, and therefore which init/probe paths can exist in a kernel image.

## Dependencies and Integration Points

The file must remain consistent with Kconfig symbol names and source filenames. It integrates with kernel build ordering, module naming, and composite object rules. Multi-object examples such as `watchdog-y` and `octeon-wdt-y` show where one logical module contains multiple translation units.

## Risks and Edge Cases

Typos between Kconfig symbol names and object mappings silently omit drivers or cause build failures. Ordering changes can matter when multiple watchdogs compete for `/dev/watchdog` or restart priority. Adding a driver without matching Kconfig dependency coverage can expose architecture-specific code to unsupported builds.

## Test Signals

Build tests with the listed symbols set to `y` and `m`, module-install checks for expected module names, and diff checks that every watchdog driver symbol in Kconfig has a corresponding object when applicable.
