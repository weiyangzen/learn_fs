<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/syncpt_hw.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/syncpt_hw.c

## Purpose

`hw/syncpt_hw.c` implements generation-specialized syncpoint hardware operations. It saves/restores syncpoint and wait-base values, loads hardware min values into atomics, performs CPU increments, assigns syncpoints to channels on protected hardware, and enables syncpoint protection.

## Important APIs, Types, And Functions

- `syncpt_restore()` and `syncpt_restore_wait_base()` write cached min/wait-base values back to registers.
- `syncpt_read_wait_base()` reads wait-base state for generations that have it.
- `syncpt_load()` atomically updates `sp->min_val` from the live hardware register and checks against tracked max.
- `syncpt_cpu_incr()` writes CPU increment bits after validating non-client-managed idle state.
- `syncpt_assign_to_channel()` programs channel ownership on HW6+.
- `syncpt_enable_protection()` enables hypervisor syncpoint protection when available.

## Control Flow

Generic syncpoint code dispatches through `host1x_syncpt_ops`. On restore, all syncpoints are unassigned from channels before min values are restored and protection is enabled. Loading loops with `atomic_cmpxchg()` to avoid races updating `min_val`. CPU increments are rejected for idle, host-managed syncpoints to avoid unexpected max/min divergence.

## State And Persistence Behavior

Software state is `min_val`, `base_val`, and assignment/locked fields in `struct host1x_syncpt`. Hardware state includes syncpoint min registers, wait-base registers, CPU increment registers, channel assignment registers, and hypervisor protection enable.

## Dependencies And Integration Points

Depends on generated sync/VM/hypervisor register macros, `syncpt.c`, `dev.h`, and channel structures. It is included into each generation unit and varies by `HOST1X_HW`.

## Risks And Test Signals

Wait bases disappear on HW7+ in this implementation, so conditional no-ops must match hardware semantics. Protection requires hypervisor registers. Tests should cover CPU increments, min/max sanity errors, save/restore across runtime PM, channel assignment, protected syncpoint access, and old wait-base relative waits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/host1x/hw/syncpt_hw.c -->
