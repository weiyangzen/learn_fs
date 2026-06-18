<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.c

## Purpose
`id.c` detects OMAP/AM/DRA silicon revision, device type, feature bits, die ID, and optional Linux soc-bus attributes. It is foundational early-boot code used by later platform, PM, erratum, and driver decisions.

## Important APIs, Types, and Functions
Public APIs include `omap_rev()`, `omap_type()`, `omap2xxx_check_revision()`, `omap3xxx_check_revision()`, `omap4xxx_check_revision()`, `omap5xxx_check_revision()`, `dra7xxx_check_revision()`, feature checkers `omap3xxx_check_features()`, `omap4xxx_check_features()`, `ti81xx_check_features()`, `am33xx_check_features()`, `omap2_set_globals_tap()`, and `omap_soc_device_init()` when `CONFIG_SOC_BUS` is enabled. Important state includes `omap_revision`, `soc_name`, `soc_rev`, `omap_features`, `tap_base`, and `tap_prod_id`.

## Control Flow
Early board setup calls `omap2_set_globals_tap()` with the initial class and TAP base. Later revision checkers read TAP IDCODE/die ID/control-module status registers, decode hawkeye/revision/package fields, set `omap_revision`, and format `soc_name`/`soc_rev`. Feature checkers read control status or fuse fields and set `omap_features`. A device initcall feeds die ID into the randomness pool. The optional soc-bus path registers machine/family/revision and a `type` attribute.

## State and Persistence Behavior
The file owns global boot-time identification state. `omap_type()` caches the device type after first detection. The die ID is not persisted by the file, but it is mixed into kernel randomness. soc-bus registration exposes immutable boot-time state through sysfs.

## Dependencies and Integration Points
It depends on CPUID reads, TAP MMIO, control-module accessors, SoC macros from `soc.h`, feature masks from `control.h`, random subsystem, and optional `linux/sys_soc.h`. Nearly every mach-omap2 subsystem depends indirectly on correct revision/type/feature detection.

## Risks
Unknown silicon falls back to latest known revisions, which can enable unsupported errata paths or low-power states. `omap2xxx_check_revision()` formats from `omap_rev()` even though it does not assign from the matched table in this body, so behavior must be checked in context. Wrong feature bits can misclassify SGX/IVA/ISP/NEON and break driver availability or PM workarounds.

## Test Signals
Boot each supported SoC family and check early `pr_info` revision strings, `/sys/devices/soc0` attributes, `omap_type()`, and feature-dependent drivers. Regression tests should cover unknown hawkeye warnings, AM35xx feature fixups, DRA7 package variants, secure/GP type decoding, and randomness feed initcall ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap2/id.c -->
