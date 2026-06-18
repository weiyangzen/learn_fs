# sources/distributed-fs/ceph-client/include/linux/hwspinlock.h

## Purpose
Defines the public hardware spinlock framework API for inter-processor or inter-core locks implemented in shared hardware.

## APIs, Control Flow, and State
Enabled builds provide registration/unregistration for lock banks, specific lock request/free, devm variants, device-tree ID lookup, lock busting, and internal trylock/timeout/unlock primitives. Inline wrappers select mode: normal disables preemption, irq disables local interrupts, irqsave preserves flags, raw leaves broader protection to the caller, and in-atomic is for atomic contexts. Timeout helpers busy-loop until success or timeout and never sleep; trylock helpers fail immediately on contention. Disabled builds intentionally let most users compile away and succeed, while registration fails/omits framework availability and specific request returns `ERR_PTR(-ENODEV)`.

## Dependencies, Integration, Risks, and Tests
Depends on device core, OF nodes, scheduler/preemption, and framework-private structs. Integrates with remoteproc, SoC mailbox/shared-resource drivers, and device-tree described hardware locks. Risks include sleeping while holding a non-raw hwspinlock, using raw mode without external serialization, long timeouts in atomic context, forgetting matching unlock mode, and treating `ERR_PTR(-ENODEV)` as a usable lock. Test signals include lock contention/timeout tests, irq/preemption state assertions, DT lookup coverage, devm cleanup, and !CONFIG compile behavior.
