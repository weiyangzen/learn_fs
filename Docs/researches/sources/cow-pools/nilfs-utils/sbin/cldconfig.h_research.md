# File Research: sources/cow-pools/nilfs-utils/sbin/cldconfig.h

## Scope

Declares NILFS cleaner daemon configuration structures, units, defaults, policy IDs, and the public configuration reader.

## Key Structures

- `struct nilfs_param` holds a parsed number plus unit.
- `enum nilfs_size_unit` defines raw, percentage, SI, and IEC units.
- `struct nilfs_cldconfig` stores GC policy, protection/check/clean/retry intervals, min/max clean segment thresholds, normal and low-space cleaning rates, mmap/set_suinfo booleans, syslog priority, and minimum reclaimable block thresholds.

## API Surface

`nilfs_cldconfig_read()` initializes a `nilfs_cldconfig` from defaults plus a configuration file, using a `struct nilfs` handle for filesystem geometry.

## Risks And Invariants

Defaults are expressed partly as percentages, so final numeric values depend on the mounted filesystem's segment and block geometry. `NILFS_CLDCONFIG_NSEGMENTS_PER_CLEAN_MAX` caps cleaning batch size at 32.
