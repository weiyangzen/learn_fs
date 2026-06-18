# sources/distributed-fs/ceph-client/drivers/thermal/thermal_thresholds.h

## Purpose
`thermal_thresholds.h` declares the user-threshold data structure and internal thermal core threshold API.

## Important APIs, Types, and Functions
`struct user_threshold` stores a list node, temperature, and direction bitmask. Prototypes cover lifecycle, handling, mutation, and iteration.

## Control Flow
There is no executable control flow in the header. It defines the contract used by netlink command handlers and thermal zone update code.

## State and Persistence Behavior
The header defines the per-threshold state shape; instances are owned by `thermal_thresholds.c` on each zone's `user_thresholds` list.

## Dependencies and Integration Points
It expects `struct thermal_zone_device` and `struct list_head` visibility from including context, normally via thermal core headers.

## Risks and Edge Cases
Because `direction` is a plain `int`, callers must pass valid `THERMAL_THRESHOLD_WAY_*` bits. API changes must be coordinated with netlink threshold command encoding.

## Test Signals
Compile coverage and the behavioral tests listed for `thermal_thresholds.c`.
