# sources/distributed-fs/ceph-client/include/linux/ratelimit_types.h

Purpose: defines the ratelimit state structure, default interval/burst constants, flags, initializers, and the `__ratelimit()` wrapper macro.

Important APIs and types: defaults are `DEFAULT_RATELIMIT_INTERVAL` of five seconds and `DEFAULT_RATELIMIT_BURST` of ten. Flags include `RATELIMIT_MSG_ON_RELEASE` and `RATELIMIT_INITIALIZED`. `struct ratelimit_state` stores a raw spinlock, interval, burst, atomic remaining count, atomic missed count, flags, and begin time. Initializer macros include `RATELIMIT_STATE_INIT_FLAGS`, `RATELIMIT_STATE_INIT`, disabled initializer, and `DEFINE_RATELIMIT_STATE`. `___ratelimit()` is the external implementation, with `__ratelimit(state)` passing `__func__`.

Control flow: static or dynamic callers initialize `ratelimit_state`, then `___ratelimit()` updates counters and determines whether an event should be emitted.

State and persistence: all state is runtime memory in each `ratelimit_state`.

Dependencies and integration points: depends on bit macros, HZ, raw spinlock types, and atomics. It is shared by printk, WARN, networking, drivers, and other throttled logging paths.

Risks and test signals: risks include initializer drift, atomic count underflow, wrong HZ-derived intervals, and disabled-state interpretation. Test static initialization, dynamic initialization, disabled interval behavior, multi-CPU contention, and suppressed message accounting.
