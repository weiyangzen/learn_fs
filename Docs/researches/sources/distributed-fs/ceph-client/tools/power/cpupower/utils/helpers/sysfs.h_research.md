# sources/distributed-fs/ceph-client/tools/power/cpupower/utils/helpers/sysfs.h

## Purpose
Declares sysfs constants and cpupower helper functions for CPU online and cpuidle state access.

## Important APIs, Types, and Functions
Defines `PATH_TO_CPU`, `MAX_LINE_LEN`, and `SYSFS_PATH_MAX`, plus prototypes for file reads, idlestate existence/read/disable/value/string access, cpuidle governor/driver getters, and scheduler getter/setter stubs.

## Control Flow, State, and Persistence
The header carries no runtime state. It defines the path and buffer-size contract used by `sysfs.c` and its consumers.

## Dependencies and Integration Points
Included by cpufreq info, cpuidle info, cpupower set/info, and helper code. The constants must stay compatible with sysfs path construction in implementations.

## Risks and Test Signals
Fixed path buffers are small for some constructed paths. The scheduler APIs are declared but unsupported by implementation. Build tests should cover all consumers and runtime tests should verify each declared function maps to an implementation.
