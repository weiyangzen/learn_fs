<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.c

## Purpose
Implements small timer utilities that use `expires == 0` as i915's canceled/inactive sentinel.

## Important APIs, types, and functions
- `cancel_timer()` deletes an active timer and writes `expires = 0`.
- `set_timer_ms()` arms a timer in milliseconds or cancels it for timeout zero.

## Control flow
`cancel_timer()` first checks `timer_active()` from the header, then calls `timer_delete()` and clears `expires`. `set_timer_ms()` converts milliseconds to jiffies, uses a compiler barrier before reading volatile `jiffies`, and calls `mod_timer()` with a nonzero expiration so zero remains reserved for canceled state.

## State and persistence
The only state touched is the caller-owned `struct timer_list`, especially `expires`.

## Dependencies and integration points
Depends on Linux jiffies/timer APIs and `i915_timer_util.h`. Intended for i915 code that wants cheap active/expired checks separate from generic timer pending state.

## Risks
The helpers assume no other code uses `expires == 0` differently for the same timer. `timer_delete()` does not guarantee callback synchronization the way shutdown/sync variants do; callers must choose the right lifetime protocol.

## Test signals
Timer unit tests, timeout-zero cancellation checks, expired-vs-pending state checks, and races around cancellation during callback execution.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.c -->
