<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ucache.conf -->
# sources/distributed-fs/orangefs/src/apps/user/ucache.conf

## Purpose
Configuration template for OrangeFS user-cache sizing and statistics constants.

## Important APIs, Types, And Functions
Defines shell-style key/value assignments: `UcacheSizeMB`, `BlocksInCache`, `LockSize`, `UCACHE_STATS_64`, and `UCACHE_STATS_16`. There are no executable functions.

## Control Flow
Any consumer must parse these variables and translate them into generated constants or runtime settings. This file itself has no includes or conditionals.

## State And Persistence
It is persistent configuration data. Values describe cache memory size, block count, lock structure size, and stats field counts that should align with `ucache.h` structures.

## Dependencies And Integration Points
Intended to integrate with the ucache build or configuration generation path and the daemon/shared-memory layout used by `ucached.c`.

## Risks And Test Signals
Risks are stale values if structure sizes change, shell quoting assumptions, and no comments documenting units beyond names. Test signals are regenerating ucache headers/config from this file and validating that daemon shared-memory sizes match expected block and lock counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/apps/user/ucache.conf -->
