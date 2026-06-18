<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lp.h -->
# sources/distributed-fs/ceph-client/include/linux/lp.h

## Purpose
This header defines internal structures and constants for the parallel printer (`lp`) driver. It bridges UAPI printer settings with kernel parport device state.

## Important APIs, Types, and Functions
Macros address `lp_table` fields, define special parport selection values, buffer size, control bits, dummy data, and delay constants. `struct lp_stats` tracks chars, sleeps, maxrun, and wakeups. `struct lp_struct` holds flags, timing, wait queues, mutex, parport device pointer, device number, buffer, and stats.

## Control Flow
The implementation uses these fields to serialize writes, wait for printer readiness, strobe data through parport control bits, and collect statistics.

## State and Persistence Behavior
State is per-minor runtime driver state in `lp_table` entries and optional stats. Printer hardware state is external. No persistence exists beyond module/device lifetime.

## Dependencies and Integration Points
It depends on wait queues, mutexes, and `uapi/linux/lp.h`. It integrates with the parport core and character device operations for `/dev/lp*`.

## Risks and Test Signals
Risks include timing-sensitive printer handshakes, stale parport pointers, buffer lifetime issues, and flag races. Test signals are parport printer writes, ioctl compatibility, wait/timeout behavior, stats inspection, and module unload while devices are idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/lp.h -->
