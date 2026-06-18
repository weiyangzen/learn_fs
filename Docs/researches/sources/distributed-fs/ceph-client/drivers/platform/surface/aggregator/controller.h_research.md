# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/controller.h

## Purpose

This internal header defines the Surface Aggregator controller's core state structures and private function interface shared between `controller.c`, `core.c`, and related SSH transport files.

## Important APIs, Types, And Functions

Important types are `ssh_seq_counter`, `ssh_rqid_counter`, `ssam_nf_head`, `ssam_nf`, `ssam_event_item`, `ssam_event_queue`, `ssam_event_target`, `ssam_cplt`, `enum ssam_controller_state`, `ssam_controller_caps`, and `ssam_controller`. The controller embeds a kref, rwsem, state enum, request transport layer, completion system, sequence/RQID counters, IRQ state, and capability values. Inline helpers bridge serdev callbacks to `ssh_ptl_rx_rcvbuf()` and `ssh_ptl_tx_wakeup_transfer()`. Prototypes expose lifecycle, notifier PM helpers, IRQ helpers, state locks, firmware/display/D0 requests, suspend/resume, and event-item cache init/destroy.

## Control Flow

The header defines the state machine used by `controller.c`: uninitialized, initialized, started, stopped, and suspended. `core.c` uses the inline receive/write-wakeup helpers from serdev callbacks and calls lifecycle/PM/IRQ functions in probe, remove, shutdown, and suspend/resume flows.

## State And Persistence

The structures describe runtime state only. Controller references are kref-managed; state transitions are guarded by the rwsem; notifiers and event queues are memory-resident and torn down with the controller. Capabilities are loaded at initialization and cached for the controller lifetime.

## Dependencies And Integration Points

The header includes Linux kref/list/mutex/rbtree/rwsem/serdev/spinlock/srcu/workqueue types, public Surface Aggregator headers, and the local SSH request layer. It connects the high-level core driver with the lower request/packet transport.

## Risks

Because this is an internal shared contract, layout or semantic changes affect multiple files. Consumers must respect lock requirements around state transitions and request submission. The `ssam_controller_receive_buf()` inline returns transport errors directly to `core.c`, which maps negative receive results to zero consumed bytes. Kref release calls back into destroy logic and assumes no unexpected outstanding users.

## Test Signals

Build coverage across PM and bus configurations, lockdep during controller state transitions, kref leak detection, serdev receive/write wakeup tests, and suspend/resume ordering with client devices validate this header's contracts.
