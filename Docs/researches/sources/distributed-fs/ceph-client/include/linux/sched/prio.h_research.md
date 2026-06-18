# sources/distributed-fs/ceph-client/include/linux/sched/prio.h

Purpose: defines scheduler priority and nice-value constants/conversion helpers.

Important APIs and types: `MAX_NICE`, `MIN_NICE`, `NICE_WIDTH`, `MAX_RT_PRIO`, `MAX_DL_PRIO`, `MAX_PRIO`, `DEFAULT_PRIO`, `NICE_TO_PRIO()`, `PRIO_TO_NICE()`, `nice_to_rlimit()`, and `rlimit_to_nice()` are the public symbols.

Control flow: scheduler policy code converts user nice values to internal static priorities, handles inverted priority ordering, and maps nice values to rlimit-style values.

State and persistence: no state is stored; these are constants and pure conversions.

Dependencies and integration points: used by scheduler classes, rlimit handling, proc/sys priority display, and nice/setpriority syscalls.

Risks and test signals: risks include off-by-one conversions, priority range ABI drift, and confusion between deadline/RT/fair ranges. Test nice/setpriority, RLIMIT_NICE, scheduler policy transitions, and boundary values -20/19.
