# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_gt_clock.c

## Purpose
Reads GT reference clock information from `RPM_CONFIG0` and provides conversion from GT clock ticks to milliseconds.

## Important APIs and Functions
- `xe_gt_clock_init` reads crystal clock frequency and CTC shift, stores `gt->info.reference_clock` and `gt->info.timestamp_base`.
- `xe_gt_clock_interval_to_ms` converts a tick count using `mul_u64_u32_div`.
- `read_crystal_clock` decodes supported 19.2, 24, 25, and 38.4 MHz crystal clock encodings and logs invalid values.

## Control Flow and State
Initialization reads one MMIO register, decodes the base frequency/timestamp base, applies the command timestamp shift, and stores results in GT info. No dynamic state is allocated.

## Dependencies and Integration Points
Called from all-forcewake GT init before engine/uC post-hwconfig work. Consumers use the stored reference clock for timing conversions.

## Risks and Test Signals
- Invalid crystal encoding stores zero frequency and timestamp base; downstream conversions would divide by zero if called without guarding, so platform tables/MMIO access must be correct.
- Platform tests should verify expected reference clock on each hardware generation.
