# sources/distributed-fs/glusterfs/xlators/features/utime/src/utime-mem-types.h

## Purpose
Defines memory-accounting categories for utime.

## Important APIs, Types, and Functions
- `enum utime_mem_types_` starts at `gf_common_mt_end + 1`.
- Categories include `utime_mt_utime_t` and `utime_mt_end`.

## Control Flow
No runtime control flow.

## State and Persistence
No state; categories feed memory accounting.

## Dependencies and Integration Points
Includes `glusterfs/mem-types.h`. Used by `utime.c` for private allocation and `mem_acct_init()`.

## Risks
Changing values can affect memory accounting reports.

## Test Signals
Compile and memory-accounting/statedump validation.
