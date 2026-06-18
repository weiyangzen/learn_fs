<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_queues.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_queues.c

## Purpose

`icssg_queues.c` provides minimal helper functions for ICSSG firmware/hardware queues backed by MIIG registers. These queues are used for descriptor pools, management commands, command responses, and timestamp responses.

## Important APIs, Types, and Functions

Exported functions are `icssg_queue_pop()`, `icssg_queue_push()`, and `icssg_queue_level()`. Local constants mirror queue count, queue data, peek, count, and reset register offsets.

## Control Flow

`icssg_queue_pop()` validates the queue index, reads queue count, returns `-EINVAL` if empty, then reads the queue data register. `icssg_queue_push()` validates the index and writes an address to the queue data register. `icssg_queue_level()` returns the count register or zero for an invalid queue.

## State and Persistence Behavior

The helpers mutate only hardware queue register state through `prueth->miig_rt`. They do not keep software shadow state, so correctness depends on firmware and callers preserving queue ownership.

## Dependencies and Integration Points

It depends on `regmap` and `struct prueth`. `icssg_config.c` uses it for FDB management messages and timestamp response buffer recycling, and queue initialization in config uses matching offsets.

## Risks and Edge Cases

Empty queue and invalid queue both return `-EINVAL` from `icssg_queue_pop()`, so callers cannot distinguish absence of data from invalid input. There is no locking; callers must ensure firmware queue ownership and sequencing. `queue` is `int` in push/level but only upper-bound checked, so negative queue numbers could compute invalid offsets if ever passed.

## Test Signals

Exercise management command send/response, timestamp queue consumption, invalid queue calls in debug/fault tests, and queue depth observations under firmware traffic. Static analysis should flag negative queue handling if external callers are added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/icssg/icssg_queues.c -->
