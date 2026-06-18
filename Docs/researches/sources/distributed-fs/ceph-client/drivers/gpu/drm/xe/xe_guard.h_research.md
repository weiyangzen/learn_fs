# sources/distributed-fs/ceph-client/drivers/gpu/drm/xe/xe_guard.h

## Purpose

`xe_guard.h` provides a small spinlock-protected guard primitive for feature exclusion. It is designed for coarse feature state arbitration where a feature can be either in exclusive active use or locked down by one or more blockers, without imposing strict owner semantics like an rwsem.

## Important APIs, Types, and Functions

- `struct xe_guard` contains `counter`, debug `name`, last `owner`, and a `spinlock_t`.
- `xe_guard_init()` initializes the spinlock, clears the counter, and records the name.
- `xe_guard_arm(guard, lockdown, who)` enters lockdown mode when `lockdown` is true or exclusive mode when false.
- `xe_guard_disarm(guard, lockdown)` releases a lockdown reference or exclusive reference and detects mismatches.
- `xe_guard_mode_str()` maps a mode flag to `"lockdown"` or `"exclusive"`.

## Control Flow

The counter encodes state: zero means idle, negative means exclusive active, positive means locked down. Lockdown arm fails with `-EBUSY` if exclusive mode is active and otherwise increments the counter. Exclusive arm fails with `-EPERM` if locked down, `-EUSERS` if already exclusive, and otherwise decrements to `-1`. Disarm validates the mode and moves the counter back toward zero.

## State and Persistence Behavior

State persists in the caller-owned `struct xe_guard`. `owner` is debug-only and records the latest successful armer; it is not cleared on disarm. All counter updates are serialized with the guard spinlock through the kernel cleanup-style `guard(spinlock)` helper.

## Dependencies and Integration Points

It depends on Linux spinlock and cleanup guard helpers, errno values, and boolean types from kernel headers. It is appropriate for feature-gating paths where lockdown and activation are incompatible but no data payload is protected.

## Risks and Edge Cases

The comments explicitly warn not to use this for data protection; it does not provide reader/writer ownership or memory lifetime semantics. Multiple lockdowns are allowed but each must be disarmed. The `owner` field can be stale after release. Error-code distinctions matter to callers that need to report "locked down" versus "already active".

## Test Signals

Tests should cover idle-to-lockdown nesting, idle-to-exclusive, lockdown blocking exclusive, exclusive blocking lockdown, double-exclusive returning `-EUSERS`, mismatched disarms returning false, and balanced disarms returning to zero.
