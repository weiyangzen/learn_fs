<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/id.c -->
# sources/distributed-fs/ceph-client/arch/arm/mach-omap1/id.c

## Purpose
Identifies OMAP1 CPU family, variant, die revision, and serial ID from hardware ID registers during early boot. The resulting `omap_revision` drives CPU feature macros used by the rest of the mach-omap1 code.

## Important APIs, Types, and Functions
Exports `omap_rev()`. Main internals are `struct omap_id`, the `omap_ids[]` lookup table, `omap_get_jtag_id()`, `omap_get_die_rev()`, and `omap_check_revision()`.

## Control Flow
`omap_check_revision()` reads JTAG ID, die revision, and OMAP32 ID, saves die IDs into `system_serial_high/low`, then refines `omap_revision` in three passes: major JTAG match, JTAG plus die revision, and full JTAG/die/omap_id match. It appends class bits for 7xx, 15xx, or 16xx and prints the detected SoC.

## State and Persistence Behavior
State is the static `omap_revision` exported through `omap_rev()` and global ARM `system_serial_*` values. It also consumes immutable hardware identity registers.

## Dependencies and Integration Points
Uses OMAP1 raw register helpers from `omap1-io.h`, addresses from `hardware.h`, and common CPU predicates in `soc.h`/`common.h`. Other files such as IRQ, mux, PM, USB, and SRAM depend on the revision result.

## Risks
Several chips have broken or ambiguous production and die ID registers, so fallback logic is critical. A missing table entry can classify only by broad family or emit `Unknown OMAP cpu type`, which can select wrong IRQ banks or SRAM size.

## Test Signals
Boot known OMAP1510, 1610/1611/5912, 1710, and 7xx hardware or emulated register sets and assert `omap_rev()` class bits and log output. Unit-style tests can stub `omap_readl()` to cover broken PROD_ID and DIE_ID fallbacks.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-omap1/id.c -->
