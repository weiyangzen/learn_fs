<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timer_types.h -->
# sources/distributed-fs/ceph-client/include/linux/timer_types.h

## Purpose
defines `struct timer_list`, the storage object for classic jiffies timers.

## Important APIs, Types, and Functions
The file is 24 lines and exports these visible symbol families: types/enums `timer_list`; macros/constants none; function-like macros none; inline helpers none; external prototypes none.

## Control Flow
The full timer API in `timer.h` initializes and queues this object; timer wheel code links it through `entry`, calls `function`, and uses `expires` plus encoded `flags` for scheduling.

## State and Persistence Behavior
Each timer stores hlist linkage, expiry jiffies, callback pointer, flags, and optional lockdep map.

## Dependencies and Integration Points
It depends on hlist and lockdep types and is included separately so structures can embed timers without pulling the full API. Direct includes are `linux/lockdep_types.h`, `linux/types.h`.

## Risks and Edge Cases
Embedding code must not copy initialized timers blindly because list linkage and lockdep state are live. Callback and flags must be initialized before arming.

## Test Signals
Compile embedding users, enable debugobjects timers, and run arm/delete/reinit lifecycle tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/timer_types.h -->
