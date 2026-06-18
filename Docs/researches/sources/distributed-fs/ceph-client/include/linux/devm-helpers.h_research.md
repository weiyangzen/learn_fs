<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devm-helpers.h -->
# sources/distributed-fs/ceph-client/include/linux/devm-helpers.h

## Purpose
Provides tiny device-managed helpers for workqueue objects that should be cancelled automatically when a driver detaches. It exists to reduce bugs caused by mixing manual work cancellation with devm-managed resources such as IRQs.

## Important APIs, Types, And Functions
The file defines `devm_delayed_work_autocancel()` and `devm_work_autocancel()`. Both initialize caller-owned work storage with `INIT_DELAYED_WORK()` or `INIT_WORK()` and register a devres action through `devm_add_action()`. The cleanup callbacks are `devm_delayed_work_drop()` and `devm_work_drop()`, which call `cancel_delayed_work_sync()` and `cancel_work_sync()`.

## Control Flow
Drivers call the helper during probe after allocating a `struct delayed_work` or `struct work_struct`. On device release, devres invokes the registered cancellation callback after normal remove processing. Cancellation synchronously drains any running callback and prevents later queued execution.

## State And Persistence
State is the initialized work item and the devres action attached to the `struct device`. There is no durable persistence. The important lifetime rule is that the work object must remain valid until devres cleanup runs.

## Dependencies And Integration Points
Depends on `linux/device.h`, `linux/workqueue.h`, and the device resource manager. It integrates with drivers that already use devm-managed IRQs, memory, clocks, or other resources and want work cancellation to share the same lifetime.

## Risks And Edge Cases
The header warns that devm cleanup may happen after `remove()` returns. If `remove()` manually frees data used by a devm-cancelled work item before devres runs, an IRQ or other source can still queue work against freed state. Callers must ensure work storage and callback dependencies outlive the devres action or explicitly order cleanup.

## Test Signals
Compile coverage is enough for the inline helpers. Runtime tests should exercise probe failure unwind, driver remove with queued work, running work during detach, and combinations with devm-managed IRQs that can schedule the work until IRQ teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/devm-helpers.h -->
