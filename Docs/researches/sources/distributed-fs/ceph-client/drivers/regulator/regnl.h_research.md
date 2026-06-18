# sources/distributed-fs/ceph-client/drivers/regulator/regnl.h

## Purpose
This private regulator header declares the netlink event emission hook used by regulator code to report regulator events by regulator name and event mask.

## Important APIs, Types, and Functions
The only API is `int reg_generate_netlink_event(const char *reg_name, u64 event);`. Include guards use `__REGULATOR_EVENT_H`, and the header carries GPL-2.0-or-later licensing.

## Control Flow
There is no executable control flow in this header. Callers include it to access the implementation-provided event generator.

## State and Persistence
The header defines no state and has no persistence behavior. Any state or side effects belong to the implementation of `reg_generate_netlink_event()`.

## Dependencies and Integration Points
It depends on standard kernel integer types for `u64` via includer context. It is an internal integration point between regulator event producers and the regulator netlink event implementation.

## Risks and Test Signals
Risk areas are declaration drift from the implementation and insufficient type includes if included from a translation unit that has not already defined `u64`. Test signals are compile coverage of all includers and runtime verification that regulator events produce expected netlink notifications.
