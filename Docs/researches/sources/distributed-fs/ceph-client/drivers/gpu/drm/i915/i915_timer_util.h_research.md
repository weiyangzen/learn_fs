<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.h

## Purpose
Declares i915 timer helpers and inline state predicates based on the timer expiration field.

## Important APIs, types, and functions
- `cancel_timer()` and `set_timer_ms()` are implemented in the C file.
- `timer_active()` returns whether `expires` is nonzero.
- `timer_expired()` returns active but not currently pending.

## Control flow
Inline predicates use `READ_ONCE()` for `expires` and generic `timer_pending()` for pending state.

## State and persistence
No state is owned here. Callers opt into `expires = 0` as inactive state.

## Dependencies and integration points
Depends on Linux timers and `READ_ONCE`. Used by i915 timeout/watchdog-style code that needs active/expired predicates.

## Risks
Directly interpreting `expires` is more specialized than generic timer APIs. Callers must keep all manipulation through compatible helpers to avoid stale active state.

## Test signals
Build coverage and timer behavior tests covering active, pending, expired, canceled, and rearmed states.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/i915_timer_util.h -->
