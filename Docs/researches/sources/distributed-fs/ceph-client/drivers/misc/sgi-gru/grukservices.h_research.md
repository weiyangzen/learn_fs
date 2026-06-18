# sources/distributed-fs/ceph-client/drivers/misc/sgi-gru/grukservices.h

Purpose: declares the kernel-service API exported by `grukservices.c` for GRU message queues, GPA access, and async GRU resource use. It is a contract for other kernel drivers that want GRU transport or copy services without managing GRU contexts directly.

Important APIs/types: `struct gru_message_queue_desc` stores the queue virtual address, global physical address, cacheline count, and optional interrupt routing fields. Message queue APIs are `gru_create_message_queue()`, `gru_send_message_gpa()`, `gru_get_next_message()`, and `gru_free_message()`. GPA helpers are `gru_read_gpa()` and `gru_copy_gpa()`. Async APIs are `gru_reserve_async_resources()`, `gru_release_async_resources()`, `gru_wait_async_cbr()`, `gru_lock_async_resource()`, and `gru_unlock_async_resource()`. Message send status codes include `MQE_OK`, `MQE_CONGESTION`, `MQE_QUEUE_FULL`, `MQE_UNEXPECTED_CB_ERR`, `MQE_PAGE_OVERFLOW`, and `MQE_BUG_NO_RESOURCES`.

Control flow: callers allocate physically contiguous, cacheline-aligned queue memory, initialize a descriptor, send one- or two-cacheline messages, and poll/free received messages in order. Async users reserve per-blade CBR/DSR resources, lock them to obtain GRU addresses, issue their own GRU instructions, wait through a supplied completion, then unlock and release.

State and persistence: the header itself has no state, but its descriptor exposes the persistent in-memory identity of a message queue. Interrupt fields couple the queue to UV cross-partition notification routes.

Dependencies and integration: includes kernel `struct completion` via the declaration context and depends on GRU cacheline/GPA semantics implemented in the C file. It is used by SGI XP UV transport to create GRU-backed activation and notification queues and by any kernel subsystem using XP/GRU cross-partition services.

Risks: comments make clear the first 32 bits of a message are reserved by the transport, so payload users can corrupt queue semantics if they treat the full payload as application-owned. The receive API requires ordered freeing and single-receiver semantics. Queue memory alignment and physical contiguity are caller obligations.

Test signals: successful use is visible through message queue behavior and the `grukservices.c` quicktests. API misuse is likely to show as message send status codes, stalled receives, or GRU fatal diagnostics.
