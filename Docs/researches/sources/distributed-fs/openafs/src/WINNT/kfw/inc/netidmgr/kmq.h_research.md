# sources/distributed-fs/openafs/src/WINNT/kfw/inc/netidmgr/kmq.h

## Purpose

`kmq.h` declares the NetIDMgr Message Queue. KMQ is the asynchronous and synchronous dispatch layer that routes typed messages to per-thread callback or window subscribers, supports ad-hoc subscription handles, call waiting, completion handlers, and error-context propagation.

## Important APIs, Types, and Functions

- `kmq_thread_id` and `kmq_timer` are Win32 `DWORD` values.
- `KMQ_WM_DISPATCH` is the window message used for HWND subscribers.
- `kmq_callback_t` is the callback signature for subscribers and plugins.
- `kmq_response` stores per-thread response payloads for scatter/gather messages.
- `kmq_message` stores type, subtype, integer and pointer parameters, sent/completed/failed counters, response list, wait event, send/expiry timers, `kherr_context`, refcount, and list links.
- `kmq_call` is a `kmq_message *` handle for posted calls.
- `kmq_message_ref` binds a message to a recipient in a queue.
- `kmq_queue` is per-thread and stores critical section, wait event, load, last post time, deleted flag, queued refs, and global list links.
- `kmq_msg_subscription` binds a message type to a callback or HWND recipient and queue.
- `kmq_msg_type` stores type ID, subscriptions, completion handler, optional name, and list links.
- APIs initialize/exit KMQ, register/find/unregister message types, subscribe/unsubscribe callbacks or windows, handle `KMQ_WM_DISPATCH`, create/delete ad-hoc subscriptions, post/send to one or many subscriptions, dispatch queued messages, broadcast post/send messages, free calls, send/post thread quit messages, enumerate responses, test/wait completion, and set completion handlers.

## Control Flow

Subscribers register by message type in the current thread. A broadcast post creates a `kmq_message`, queues message references on each subscriber thread's `kmq_queue`, signals the queues, and returns immediately unless the caller requested a call handle. Synchronous send posts and waits for all recipients. Threads without Windows message loops call `kmq_dispatch(timeout)` to process queued refs. Threads with windows subscribe HWNDs and process `KMQ_WM_DISPATCH` via `kmq_wm_begin`/`end` or `kmq_wm_dispatch`. Completion handlers run after all instances of a message type complete and before message cleanup.

## State and Persistence Behavior

KMQ state is in-process and per-thread: queues, subscriptions, message refs, refcounted messages, wait events, and completion handlers. It is not persisted across sessions. Messages can carry `kherr_context` so async work remains associated with the originating error context. Call handles must be freed with `kmq_free_call()` after waiting or inspection.

## Dependencies and Integration Points

`kmq.h` depends on `khdefs.h`, `khlist.h`, `kherr.h`, Win32 synchronization/window types, and standard message IDs from `khmsgtypes.h`. It is central to KMM plugin message processors (`kmm_plugin_reg.msg_proc`), credential acquisition, alerts, action updates, KCDB notifications, and identity-provider dispatch.

## Risks and Edge Cases

- Subscriptions are per-thread; subscribing the same callback in multiple threads intentionally creates multiple deliveries.
- Callback unsubscribe only removes subscriptions for the current thread, so cleanup must run in the subscribing thread.
- Window subscribers must unsubscribe before window destruction to avoid dispatch to dead HWNDs.
- Synchronous sends can deadlock if a recipient thread is not dispatching or waits back on the sender.
- More than one waiter on a call is serialized by call freeing behavior; callers should avoid sharing call handles casually.
- Completion handler spelling parameter `hander` is harmless but highlights that only one handler exists per type and later calls overwrite it.

## Test Signals

- Broadcast to multiple callback and HWND subscribers across threads and verify sent/completed/failed counts.
- Test `kmq_send_message()` partial failure when one subscriber returns error.
- Create ad-hoc subscriptions and send targeted messages without broadcast delivery.
- Exercise quit messages causing `kmq_dispatch()` to return `KHM_ERROR_EXIT`.
- Wait/free call handles under timeout, already-completed, and multi-waiter cases.
- Verify completion handlers release payloads and can enqueue follow-up messages safely.
