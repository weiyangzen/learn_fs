## sources/distributed-fs/ceph-client/arch/arm/mm/l2c-common.c

### Purpose
Provides a shared helper to disable the outer/L2 cache under strict CPU and interrupt conditions.

### Important APIs, Types, And Functions
Single function: `outer_disable`. It checks interrupts are disabled and only one CPU is online, then calls `outer_cache.disable` if supplied.

### Control Flow
The helper is synchronous and has no retry or state machine. It is meant for shutdown/suspend/reset-style contexts where other CPUs cannot use the cache concurrently.

### State, Dependencies, And Integration
No local state. Depends on `outer_cache` ops and SMP CPU online count. Integrates with platform L2 cache controller power management.

### Risks And Test Signals
Risks include disabling L2 while interrupts or secondary CPUs are active, which could corrupt memory or hang. Test suspend/resume and shutdown paths with lockdep/WARN monitoring and CPU hotplug preconditions.
