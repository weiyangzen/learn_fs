<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.h -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.h

## Purpose

`syncpt.h` defines internal host1x syncpoint and wait-base structures plus helper APIs for allocation, state queries, save/restore, expiration checks, and max/min accounting.

## Important APIs, Types, And Functions

- `struct host1x_syncpt_base`: wait-base ID and allocation flag.
- `struct host1x_syncpt`: kref, ID, atomic min/max, wait-base value, name, client-managed flag, host pointer, optional base, fence list, and timeout lock flag.
- Inline helpers check max sanity, client-managed mode, idle state, valid ID, and set locked state.
- Prototypes expose init/deinit, counts, load, wait-base load, save/restore, expiration, and max increment.

## Control Flow

Most logic is inline predicates. `host1x_syncpt_is_expired()` and related APIs are implemented in `syncpt.c`/`syncpt_hw.c`.

## State And Persistence Behavior

The structures are allocated for the host lifetime. Atomic min/max and fence lists are mutated by submission, interrupts, waits, and PM paths.

## Dependencies And Integration Points

Includes public `<linux/host1x.h>`, atomic/kref primitives, `fence.h`, and `intr.h`. It is central to CDMA, channel, interrupts, debug, and client APIs.

## Risks And Test Signals

Idle and max sanity checks skip client-managed syncpoints by design. Build coverage, wraparound tests, and suspend/resume tests validate this header's invariants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.h -->
