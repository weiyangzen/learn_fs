# sources/distributed-fs/ceph-client/drivers/net/eql.c

## Purpose
This file implements the legacy Equalizer load balancer for serial network interfaces. It creates a master `eql` netdev and uses private ioctls to attach slave devices, then transmits each skb through the currently least-loaded live slave.

## Important APIs, Types, and Functions
- `eql_setup()` initializes master private state, timer, slave queue, flags, ARPHRD type, MTU, and netdev ops.
- `eql_timer()` decays queued-byte estimates by priority and removes down slaves.
- `__eql_schedule_slaves()` selects the best live slave by load metric.
- `eql_slave_xmit()` rewrites `skb->dev`, updates queued bytes, and calls `dev_queue_xmit()`.
- Private ioctl handlers enslave/emancipate devices and get/set slave or master configuration.
- `eql_kill_one_slave()` releases a slave netdev reference, clears `IFF_SLAVE`, and frees the slave record.

## Control Flow
Module init allocates and registers `eql`. Open starts the timer and initializes slave limits. Privileged userspace attaches slaves with `EQL_ENSLAVE`; the driver copies the request, looks up the device in `init_net`, rejects master/slave devices, allocates state, and inserts it under a spinlock. Transmit schedules a slave or drops the skb if none is usable. Close synchronously deletes the timer and clears all slaves.

## State and Persistence
`equalizer_t` owns timer and queue state; each `slave_t` stores the slave device, priority, byte-per-second priority, queued-byte estimate, and netdev reference tracker. Configuration is runtime-only and not persisted beyond module lifetime.

## Dependencies and Integration Points
The driver depends on `linux/if_eql.h`, private netdev ioctls, `CAP_NET_ADMIN`, timers, spinlocks, user-copy helpers, and netdevice transmit APIs.

## Risks and Edge Cases
Compat syscalls are unsupported. The driver mutates `IFF_SLAVE` directly and is much older than bonding/team. The load metric is approximate and timer-decayed. Transmit calls `dev_queue_xmit()` while holding the queue lock, a historical pattern worth checking against modern locking assumptions.

## Test Signals
Check ioctl permission handling, enslave/emancipate, duplicate replacement, max-slave enforcement, priority changes, transmit distribution, down-slave cleanup, close cleanup, and compat rejection.
