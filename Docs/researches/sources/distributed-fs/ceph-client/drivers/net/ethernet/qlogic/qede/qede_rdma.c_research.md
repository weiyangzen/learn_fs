# sources/distributed-fs/ceph-client/drivers/net/ethernet/qlogic/qede/qede_rdma.c

## Purpose
This file implements the glue between the Ethernet qede driver and the separate qedr RDMA driver. It tracks RDMA-capable qede devices, lets the qedr module register/unregister callbacks, creates a per-device workqueue for asynchronous RDMA notifications, and forwards qede netdev lifecycle events such as up/down/close/MAC change/MTU change to qedr.

## Important APIs, Types, and Functions
Global state is `qedr_drv`, `qedr_dev_list`, and `qedr_dev_list_lock`. Per-device state is under `edev->rdma_info`, including list entry, `qedr_dev`, workqueue, event list, kref, completion, and `exp_recovery`.

Driver-facing exported APIs are `qede_rdma_register_driver()` and `qede_rdma_unregister_driver()`. qede lifecycle APIs are `qede_rdma_supported()`, `qede_rdma_dev_add()`, `qede_rdma_dev_remove()`, `qede_rdma_dev_event_open()`, `qede_rdma_dev_event_close()`, `qede_rdma_event_changeaddr()`, and `qede_rdma_event_change_mtu()`. Internal helpers dispatch add/remove/open/close/shutdown/change notifications and manage queued `struct qede_rdma_event_work` nodes.

## Control Flow
When qede probes a supported device, `qede_rdma_dev_add()` creates a single-thread RDMA workqueue, initializes event tracking, adds the device to the global list, and calls the currently registered qedr driver's `add()` callback if present. During normal removal, qede destroys the event workqueue, removes the qedr device unless recovery already did so, clears `qedr_dev`, and deletes the list entry. Recovery removal avoids full workqueue teardown and marks `exp_recovery` to suppress later event enqueueing.

When qedr registers, it becomes the singleton `qedr_drv`, and every qede device already on the list is added to qedr; devices whose netdev is running and operational also receive `QEDE_UP`. When qedr unregisters, each attached non-recovery device is removed and the singleton pointer is cleared.

Asynchronous events are added with `qede_rdma_add_event()`. It rejects recovery and missing-device cases, takes a kref unless destruction has begun, reuses an idle event node or allocates one with `GFP_ATOMIC`, initializes work, queues it to the per-device workqueue, and drops the kref. The work handler maps event enums to the appropriate qedr `notify()` calls.

## State and Persistence Behavior
State is in-memory only. The global driver pointer and device list persist while modules are loaded. Per-device work nodes remain on `rdma_event_list` and are reused when not pending. `kref` and `event_comp` coordinate workqueue destruction with concurrent event creation. `exp_recovery` records that expected recovery is in progress and suppresses events or duplicate qedr removal.

## Dependencies and Integration Points
It depends on `linux/qed/qede_rdma.h` for `struct qedr_driver` and event enums, qede device state, netdev operational state, workqueues, lists, mutexes, krefs, and completions. It is called from qede probe/remove, link open/close updates, netdev MAC change notifier, and MTU change paths. It exports registration symbols for the qedr module.

## Risks
The main risks are concurrency and lifetime errors between qede removal, queued RDMA events, and qedr unregister. Event nodes are reused based on `work_pending()`, so correctness relies on the single-thread workqueue and cleanup flushing before freeing nodes. Recovery mode intentionally skips some normal teardown; wrong `exp_recovery` transitions could either leak qedr devices or notify a partially removed qedr instance. Global list operations are protected by one mutex, but event enqueue uses per-device fields outside that mutex and depends on kref destruction coordination.

## Test Signals
Test RDMA-capable and non-RDMA hardware paths, qede probe before and after qedr module load, qedr unload while qede devices exist, interface up/down/link changes, MAC and MTU changes, normal remove, and firmware recovery. Useful signals include correct qedr add/remove/notify counts, no events after workqueue destruction, no list corruption, no use-after-free during concurrent unregister and netdev close, and no RDMA actions for unsupported devices.
