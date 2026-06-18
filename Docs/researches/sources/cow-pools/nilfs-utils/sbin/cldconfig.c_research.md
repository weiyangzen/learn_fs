# File Research: sources/cow-pools/nilfs-utils/sbin/cldconfig.c

## Scope

Parses `nilfs_cleanerd.conf`, initializes default cleaner daemon settings, converts user units to filesystem-relative segment/block counts, and logs invalid configuration lines.

## APIs And Behavior

- Token parsing skips whitespace, supports comments beginning with `#`, and limits lines to `LINE_MAX` and tokens to `NTOKENS_MAX`.
- Numeric parsers handle unsigned integers, fractional seconds, size suffixes, and percentages.
- Size units support SI and IEC suffixes from kB/KiB through EB/EiB, plus raw counts and percentages.
- Segment thresholds convert percentages against `nilfs_get_nsegments()` and byte sizes against `block_size * blocks_per_segment`.
- Reclaimable-block thresholds convert raw, percent, or byte values to blocks per segment and clamp overlarge values.
- Keyword handlers support protection period, min/max clean segments, check/clean/retry intervals, timestamp selection policy, normal and low-space GC rates, mmap/set_suinfo toggles, log priority, and reclaimable-block thresholds.
- `nilfs_cldconfig_set_default()` computes defaults using the active NILFS geometry.
- `nilfs_cldconfig_read()` verifies the path is a regular file, loads defaults, parses overrides, and returns success even when individual invalid keywords only produced warnings.

## State And Dependencies

The parser writes `struct nilfs_cldconfig`, calls NILFS geometry accessors, and reports through `syslog`. It is consumed by `cleanerd.c`.

## Risks And Invariants

Most keyword handler parse failures are warning-tolerant and leave the previous/default value in place. `use_mmap` and `use_set_suinfo` are enable-only flags in the configuration grammar. Byte-unit conversions use unsigned arithmetic and do not explicitly detect overflow for very large suffix values.
