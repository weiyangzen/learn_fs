# File Research: sources/block-storage/parted/libparted/labels/aix.c

Purpose: Minimal AIX disk-label backend with probing support and unsupported operation stubs.

Main interfaces: Registers `PedDiskType` named `aix`. `aix_probe()` checks sector 0 for big-endian magic `0xc9c2d4c1`. Standard disk and partition callbacks are present through `pt-common.h`.

Control flow: Allocation creates an empty `PedDisk`; duplicate creates a fresh empty AIX disk. Read, write, partition creation, duplication, system setting, and flag setting throw `PED_EXCEPTION_NO_FEATURE` and fail. Max supported partitions is reported as 16, while max primary count returns 4.

Dependencies: Uses libparted disk abstractions, endian helpers, `pt-tools.h`, and generated limit functions from `pt-common.h`.

Important details and risks: This backend can recognize AIX labels but cannot safely inspect or modify them. Any user path expecting actual AIX partition enumeration will receive an unsupported error. Tests should verify probe behavior and that mutation/read APIs fail cleanly without partial state.
