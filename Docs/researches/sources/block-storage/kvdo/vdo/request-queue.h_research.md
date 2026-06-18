# File Research: sources/block-storage/kvdo/vdo/request-queue.h

Public interface for the UDS worker request queue.

Defines:
- Opaque `struct uds_request_queue`.
- `uds_request_queue_processor_t`, a callback that processes one `struct uds_request` and handles its own errors.

Exports:
- `make_uds_request_queue()` to allocate a queue and start its worker.
- `uds_request_queue_enqueue()` to enqueue normal or requeued requests.
- `uds_request_queue_finish()` to shut down, drain, join, and free the queue.

The header documents that requeued requests are usually processed ahead of normal requests, but exact ordering is not absolute under concurrent producer races.
