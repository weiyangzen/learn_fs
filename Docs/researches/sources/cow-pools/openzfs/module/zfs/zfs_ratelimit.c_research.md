# File Research: sources/cow-pools/openzfs/module/zfs/zfs_ratelimit.c

## Summary
Provides a small ZFS-owned rate limiter used instead of the Linux kernel `__ratelimit()` helper because the kernel helper emits unwanted suppression messages.

## Main Responsibilities
- Initialize and destroy `zfs_ratelimit_t`.
- Track event count within a fixed interval.
- Return whether the caller should proceed or suppress the event.

## Key APIs
- `zfs_ratelimit_init()`.
- `zfs_ratelimit_fini()`.
- `zfs_ratelimit()`.

## Important Behavior
The limiter stores a pointer to the live burst value rather than copying it, allowing module parameters or other callers to adjust the threshold after initialization. `zfs_ratelimit()` increments `count` under `rl->lock`, resets the interval when `NSEC2SEC(now - start) >= interval`, and returns `0` when the count reaches or exceeds `*burst` before the interval expires.

## Dependencies
Uses ZFS kernel compatibility primitives: `mutex_init()`, `mutex_enter()`, `gethrtime()`, and `NSEC2SEC()`.

## Risks
The first event after an interval reset sets `count` to zero after incrementing, effectively restarting the accounting window. A burst value of zero suppresses all events in an active interval after the initial reset behavior.
