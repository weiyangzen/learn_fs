
# sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-async.c

Purpose: manages OPAL asynchronous operation tokens and completion delivery through OPAL message notifiers.

Important APIs/types/functions: `enum opal_async_token_state` tracks unallocated, allocated, dispatched, abandoned, and completed tokens. Exported APIs are `opal_async_get_token_interruptible()`, `opal_async_release_token()`, `opal_async_wait_response()`, and `opal_async_wait_response_interruptible()`. `opal_async_comp_event()` handles `OPAL_MSG_ASYNC_COMP` messages, and `opal_async_comp_init()` initializes token count from device tree.

Control flow: init reads `/ibm,opal` property `opal-msg-async-num`, allocates the token array, registers a notifier, and initializes a semaphore to the token count. Token allocation waits on the semaphore then marks a free token allocated under spinlock. Callers issuing an OPAL async call must wait at least once after `OPAL_ASYNC_COMPLETION`; interruptible wait marks an allocated token dispatched so signal-aborted callers can safely release it. Completion messages mark tokens completed, copy the response, wake waiters, or free abandoned tokens.

State and persistence: state is an in-memory token array, semaphore, waitqueue, and completion spinlock. No persistent state.

Dependencies and integration points: depends on OPAL message infrastructure, `opal_wake_poller()`, device tree, waitqueues, semaphores, and clients of async OPAL calls.

Risks: completion handler trusts firmware token values and indexes the token array after parsing the message. Caller ordering is strict: if an async OPAL call completes asynchronously, the caller must wait before further async token operations. Abandoned-token handling prevents leaks after interruptible waits but is sensitive to state transitions.

Test signals: concurrent token exhaustion, signal-interrupted waits, abandoned completion freeing, notifier registration failure, invalid token argument checks, and OPAL async clients receiving response payloads.
