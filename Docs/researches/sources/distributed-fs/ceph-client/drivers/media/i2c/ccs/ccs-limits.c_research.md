# sources/distributed-fs/ceph-client/drivers/media/i2c/ccs/ccs-limits.c

## Purpose
`ccs-limits.c` is a generated table that maps logical CCS limit IDs to physical CCS/CCI registers, byte spans, grouping flags, and human-readable names. `ccs-core.c` uses it to bulk-read sensor capabilities into a compact cache.

## Important APIs, Types, and Functions
The single exported object is `const struct ccs_limit ccs_limits[]`. Each entry contains a `CCS_R_*` register macro, size in bytes, flags such as `CCS_L_FL_SAME_REG`, and a name. A zeroed guardian terminates the table.

## Control Flow
There is no executable control flow. At module init, `ccs-core.c` iterates this table to build `ccs_limit_offsets[]`. During probe, `ccs_read_all_limits()` iterates the table again, reads each register range, stores values into `sensor->ccs_limits`, and skips repeated logical offsets when `CCS_L_FL_SAME_REG` is set.

## State and Persistence Behavior
The table is immutable kernel data. It describes volatile sensor capability/register state but does not store per-device state. Cached values live in each `ccs_sensor`.

## Dependencies and Integration Points
It includes generated `ccs-regs.h` for register macros and `ccs-limits.h` for `struct ccs_limit`. It must stay synchronized with `CCS_L_*` IDs and offset macros in `ccs-limits.h`.

## Risks and Edge Cases
Generated table/header drift would make `ccs_limit_offsets[]` point at wrong data. `CCS_L_FL_SAME_REG` entries for split lane bitrate arrays rely on core offset logic to accumulate size without advancing the logical limit counter. Sizes must be multiples of register width for correct iteration.

## Test Signals
Module init should pass its `WARN_ON()` checks for guardian and `CCS_L_LAST` count. Probe logs with dynamic debug should show sane values for every named limit. Hardware validation should cover multi-register limits such as frame descriptors, binning subtypes, HDR subtypes, and per-lane bitrate arrays.
