<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.c

## Purpose

`syncpt.c` manages host1x syncpoint allocation, min/max shadow accounting, wait-base allocation, CPU increments, waits through DMA fences, save/restore across PM, and special VBLANK syncpoint reservations.

## Important APIs, Types, And Functions

- `host1x_syncpt_alloc()` / `host1x_syncpt_request()` allocate exclusive syncpoints, optional wait bases, names, and client-managed state.
- `host1x_syncpt_put()` releases syncpoints, resets max to current hardware value, frees wait bases and names, and clears lock/client flags.
- `host1x_syncpt_incr_max()`, `host1x_syncpt_read_max()`, `host1x_syncpt_read_min()`, and `host1x_syncpt_load()` maintain shadow max/min values.
- `host1x_syncpt_wait()` waits on a threshold using a host1x fence and supports polling/no-timeout behavior.
- `host1x_syncpt_save()` / `host1x_syncpt_restore()` preserve syncpoint state over runtime PM and re-enable protection.
- Lookup helpers get syncpoints by ID with or without a reference; vblank reservation release frees boot-reserved syncpoints 26/27 on older SoCs.

## Control Flow

Initialization allocates arrays for syncpoints and wait bases, assigns IDs, initializes the syncpoint mutex, reserves a NOP syncpoint, and optionally reserves VBLANK syncpoints. Allocation scans for the first zero kref, optionally claims a wait base, names the syncpoint, sets client-managed mode, and initializes the kref under `syncpt_mutex`. Waiting first loads current hardware state, returns immediately if expired, maps negative timeout to effectively infinite, creates a fence, waits, cancels on timeout, reloads the value, and verifies actual expiration.

## State And Persistence Behavior

Each syncpoint persists an ID, kref, atomic min/max shadows, base value, name, client-managed flag, host pointer, optional wait base, fence list, and locked flag. Hardware syncpoint values persist in registers and are restored from shadow during resume. VBLANK reservations use synthetic krefs until released by display code.

## Dependencies And Integration Points

Depends on hardware syncpoint ops, fence/interrupt code, tracepoints, DMA fences, and public host1x client APIs. Channel submission increments max and assigns syncpoints; timeout paths can lock failed syncpoints.

## Risks And Test Signals

32-bit wrap comparisons must remain consistent across wait, interrupt, and expiry checks. Host-managed syncpoints should be idle before suspend. Wait cancellation uses the fence timeout path. Tests should cover allocation exhaustion, wait bases, client-managed syncpoints, CPU increments, timeout waits, wraparound thresholds, vblank reservation release, runtime PM save/restore, and locked syncpoint rejection in CDMA.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/syncpt.c -->
