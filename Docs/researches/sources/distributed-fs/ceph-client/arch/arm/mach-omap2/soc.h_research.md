# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/soc.h

## Purpose
Defines OMAP2+ SoC identity, revision, class/subclass/package detection macros, feature flags, revision constants, and OMAP-scoped initcall wrappers.

## APIs, Flow, And State
Declares `omap_type()` and `omap_rev()`, then derives class, AM/TI/DRA class, subclass, package, and specific type predicates through macro-generated inline functions. Kconfig-controlled `soc_is_*()` macros default to `0` and are selectively redefined when a SoC family is enabled. Revision constants encode OMAP242x/243x/343x/363x, TI81xx, AM35xx/33xx/43xx, OMAP443x/446x/447x/54xx, and DRA7xx variants. Feature state is global `omap_features`, with helpers such as `omap3_has_io_wakeup()`, `omap3_has_sdrc()`, and `omap4_has_perf_silicon()`. `omap_*_initcall()` wrappers skip init functions when a multiplatform kernel is booted on a non-OMAP SoC. Legacy `cpu_is_*()` macros alias modern `soc_is_*()`.

## Dependencies And Integration
Includes per-family ID headers, Linux bitops, and OF support. Used throughout PRM/CM/PM/SDRC code to select SoC-specific register layouts and errata paths.

## Risks And Test Signals
The macro layering is compile-time and runtime dependent; wrong `omap_rev()` encoding or Kconfig guard can disable valid SoC paths or enable invalid ones. Test signals are revision detection during boot, correct SoC-specific PRM init data selection, feature-dependent IO wake/SDRC behavior, and initcalls not running on non-OMAP multiplatform boots.
