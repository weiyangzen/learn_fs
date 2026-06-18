# sources/distributed-fs/ceph-client/include/linux/rcuref.h

## Purpose

`rcuref.h` defines an RCU-aware reference counter for objects that can be looked up locklessly while their memory remains stable under RCU. It provides reference acquisition, release, dead-state detection, and saturation zones designed to tolerate races around final put operations.

## Important APIs, Types, and Functions

The counter type is `rcuref_t`, defined elsewhere as an atomic wrapper. Encoded zones include `RCUREF_ONEREF`, `RCUREF_MAXREF`, `RCUREF_SATURATED`, `RCUREF_RELEASED`, `RCUREF_DEAD`, and `RCUREF_NOREF`. The stored atomic value is one less than the public reference count for normal live counts.

`rcuref_init()` initializes the count. `rcuref_read()` reports live references and returns zero for released/dead zones. `rcuref_is_dead()` detects counters that have passed the final-release transition. `rcuref_get()` increments unless the object is already being released or dead, delegating rare saturation/dead-zone cases to `rcuref_get_slowpath()`.

`rcuref_put_rcusafe()` and `rcuref_put()` release a reference and return true only when the caller may deconstruct or schedule deconstruction. `rcuref_put()` disables preemption around the common implementation so an RCU grace period cannot pass during the race-sensitive slow path; `rcuref_put_rcusafe()` requires the caller to already be in an RCU-safe or atomic context.

## Control Flow

The get path unconditionally adds one with relaxed ordering. Normal nonnegative results succeed immediately; negative results indicate saturation or death-zone values and are repaired or rejected by the slow path.

The put path subtracts one with release ordering. A nonnegative result means other references remain. Negative results include the final drop and special zones; `rcuref_put_slowpath()` determines whether the counter can be moved to released/dead state or whether a concurrent get/put race prevents final deconstruction.

## State and Persistence Behavior

All state is the encoded atomic counter. The counter can move from live counts to saturation on overflow and to released/dead/no-reference zones near object teardown. It does not persist beyond the lifetime of the protected object, but its state determines when the object can be freed after RCU grace periods.

## Dependencies and Integration Points

The header depends on atomic operations, lockdep RCU checks, preemption control, and RCU read-side state. It integrates with `lib/rcuref.c` slow paths and is intended for objects using RCU or equivalent lifetime stabilization during lockless lookup.

## Risks

Calling `rcuref_get()` without a guarantee that object memory is stable can race with free. Calling `rcuref_put_rcusafe()` outside an RCU read-side or otherwise atomic context trips `RCU_LOCKDEP_WARN()` and can allow a grace period to pass during final-put races. Ignoring a false `rcuref_put()` return can prematurely deconstruct an object. Saturation leaks are deliberate protection against wraparound but can hide reference leaks.

## Test Signals

Stress tests should race `rcuref_get()` and `rcuref_put()` around the last reference under RCU lookup, verify dead-state detection, exercise saturation/overflow warning paths, and run with lockdep/preemption debugging to catch unsafe `rcuref_put_rcusafe()` callers.
