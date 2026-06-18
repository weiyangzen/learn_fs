<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_regmap.h -->
# sources/distributed-fs/ceph-client/include/sound/sdca_regmap.h

## Purpose
`sdca_regmap.h` declares helpers that translate parsed SDCA control metadata into regmap policy and initialization behavior.

## Important APIs, types, and functions
The policy predicates are `sdca_regmap_readable()`, `sdca_regmap_writeable()`, `sdca_regmap_volatile()`, `sdca_regmap_deferrable()`, and `sdca_regmap_mbq_size()`. Initialization helpers are `sdca_regmap_count_constants()`, `sdca_regmap_populate_constants()`, `sdca_regmap_write_defaults()`, and `sdca_regmap_write_init()`.

## Control flow
After `sdca_parse_function()` builds control descriptors, regmap setup calls the predicate helpers to decide access permissions, volatility, deferred access, and multi-byte quantity sizing. Constant/default values are counted and populated for regcache defaults, then default and initialization writes are sent to hardware.

## State and persistence behavior
The header owns no state. Implementations consume `sdca_function_data` and write hardware/regcache state according to parsed defaults and init tables. Defaults may persist in regcache during runtime but are not stored on disk.

## Dependencies and integration points
It depends on `struct regmap`, `struct reg_default`, devices, and SDCA function metadata. It links parser output to Linux regmap and ASoC component register access.

## Risks and test signals
Risks include misclassifying RW1C/RW1S/DC controls, caching volatile status bits, writing defaults for fixed or read-only controls, wrong MBQ sizing for multi-byte SDCA controls, and initialization sequencing before interrupts are masked. Test signals include regmap access table checks, default-cache population, volatile readback, deferred-control handling, and init-table write failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/sound/sdca_regmap.h -->
