# sources/distributed-fs/ceph-client/include/linux/workqueue_api.h

## Purpose
`workqueue_api.h` is a forwarding header for the Linux workqueue API. It contains only `#include <linux/workqueue.h>`, allowing code to depend on an API-named include while receiving the complete workqueue interface.

## Important APIs, Types, and Functions
The file defines no independent symbols. Through `workqueue.h`, consumers see `struct work_struct`, `struct delayed_work`, `struct rcu_work`, workqueue flags, initialization macros, queueing, flushing, cancellation, allocation, and system workqueue declarations.

## Control Flow
There is no runtime control flow. Compile-time inclusion pulls in `workqueue.h`.

## State and Persistence
No state is owned by this header. All state behavior is inherited from workqueue structures and implementation files described by `workqueue.h`.

## Dependencies and Integration Points
The only direct dependency is `linux/workqueue.h`. It integrates with source files that want a stable API include boundary for deferred work.

## Risks
Consumers should not assume this is a reduced dependency surface; it imports the full workqueue header. Any workqueue API or include-order change affects this shim. Static analysis should resolve it to the full workqueue contract.

## Test Signals
Compile tests are the meaningful signal: code including `linux/workqueue_api.h` should build and have access to the same workqueue APIs as code including `linux/workqueue.h`.
