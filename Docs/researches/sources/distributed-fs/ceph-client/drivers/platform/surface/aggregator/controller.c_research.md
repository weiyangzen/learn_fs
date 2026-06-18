# sources/distributed-fs/ceph-client/drivers/platform/surface/aggregator/controller.c

## Purpose

This source implements the main Surface System Aggregator Module controller: SSH sequence/request ID allocation, event notification dispatch, event activation reference counting, asynchronous event completion, controller lifecycle/state transitions, synchronous request submission, internal SAM requests, notifier registration, and wakeup IRQ management.

## Important APIs, Types, And Functions

Important exported APIs include `ssam_controller_init/start/shutdown/destroy`, `ssam_controller_get/put`, `ssam_controller_statelock/stateunlock`, `ssam_request_write_data()`, `ssam_request_sync_alloc/free/init/submit`, `ssam_request_do_sync()`, `ssam_request_do_sync_with_buffer()`, `ssam_get_firmware_version()`, display/D0 notification helpers, notifier register/unregister/event enable/disable functions, `ssam_notifier_disable_registered()`, `ssam_notifier_restore_registered()`, and IRQ setup/free/arm/disarm. Key private systems are `ssh_seq_counter`, `ssh_rqid_counter`, SRCU notifier heads, RB-tree event refcounts, the `ssam_cplt` workqueue, controller capability loading via ACPI `_DSM` or OF defaults, and `ssam_handle_event()`.

## Control Flow

Initialization loads controller capabilities, resets counters, creates the completion workqueue/notifier system, initializes the request transport layer, and enters `INITIALIZED`. Start launches the transport layer and enters `STARTED`. Requests are serialized by `ssam_request_write_data()` through `ssh_msgb.h`, submitted to the request transport, completed by callbacks, and copied into caller response buffers. Incoming events are allocated, routed by target ID and event RQID to a completion queue, then processed in bounded workqueue batches through registered notifiers. Shutdown flushes the transport, drains completions, unregisters notifiers, shuts down the request layer, and enters `STOPPED`.

## State And Persistence

State includes the controller kref, rwsem-protected state machine, transport layer, completion queues, notifier SRCU lists, event refcount RB-tree, sequence/RQID counters, IRQ number/wakeup flag, and capability values. No disk persistence exists. EC-side event enables, display/D0 state, and pending requests persist in firmware until explicitly changed, reset, or power-state transition.

## Dependencies And Integration Points

The controller depends on ACPI, GPIO, IRQ, serdev, workqueues, SRCU, rbtrees, unaligned little-endian helpers, public Surface Aggregator controller/serial-hub headers, local SSH request layer, `ssh_msgb.h`, and tracepoints. It is driven by `core.c` and consumed by SSAM bus clients and non-bus clients.

## Risks

Request submission only performs a superficial `STARTED` check; callers must hold lifecycle guarantees or use device links. Notifier enable/disable has EC side effects while holding the notifier lock, so slow firmware can stall registration paths. Wake IRQ event release is explicitly incomplete; the handler only acknowledges and comments describe missing GPIO callback processing. Refcount mismatch or inconsistent flags can leave firmware events enabled or disabled unexpectedly. Hibernation paths rely on disable/restore of registered events. Large event payloads allocate dynamically and require robust memory-pressure behavior.

## Test Signals

Validation should cover request/response success, timeout/error paths, response-buffer-too-small handling, concurrent request ID allocation, event notifier priority/stop/handled bits, duplicate register/unregister, event refcount enable/disable sequencing, suspend/resume/freeze/thaw/poweroff/restore, wake IRQ arm/disarm, shutdown with active requests/events, and error injection through `SURFACE_AGGREGATOR_ERROR_INJECTION`.
