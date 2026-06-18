# sources/distributed-fs/ceph/src/rgw/rgw_dmclock.h

## Purpose
Defines RGW dmClock scheduling basics: client classes, imported dmClock types, scheduler selection enum, and config-based scheduler type lookup.

## Important APIs, types, and functions
`client_id` classifies RGW traffic as `admin`, `auth`, `data`, or `metadata`. `Cost` and `ClientInfo` alias crimson dmClock types. `scheduler_t` distinguishes no scheduler, simple throttler, and dmClock. `get_scheduler_t()` reads `rgw_scheduler_type`.

## Control flow
RGW initialization reads scheduler config, builds context/scheduler objects accordingly, and request paths classify work by `client_id`.

## State and persistence
No persistent state. This header defines enum values that must match counter arrays and client config ordering.

## Dependencies and integration points
Depends on the dmClock submodule and Ceph config. It is shared by async/sync scheduler implementations and scheduler context.

## Risks and test signals
Adding client classes requires updating static assertions, counters, config readers, and arrays. Tests should cover config strings `dmclock`, `throttler`, unknown/none, and mapping of each client class to configured reservations/weights/limits.
