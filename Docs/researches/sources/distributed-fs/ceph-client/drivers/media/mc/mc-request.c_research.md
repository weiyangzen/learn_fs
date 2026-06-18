# sources/distributed-fs/ceph-client/drivers/media/mc/mc-request.c

Purpose: media request API implementation. It allocates request file descriptors, queues requests through driver validation/queue ops, supports poll/reinit/close, manages request object binding/completion/unbinding, and tracks request/request-object counters.

Important APIs/types/functions: exported functions include `media_request_put()`, `media_request_get_by_fd()`, `media_request_alloc()`, `media_request_object_find()`, `media_request_object_put()`, `media_request_object_init()`, `media_request_object_bind()`, `media_request_object_unbind()`, `media_request_object_complete()`, and `media_request_manual_complete()`. Internal ioctl paths are `media_request_ioctl_queue()` and `media_request_ioctl_reinit()`.

Control flow: allocation creates a request through optional driver `req_alloc`, initializes state/list/lock/waitqueue/kref, creates an anonymous inode fd, stores the request in file private data, and publishes the fd. Queue serializes with `mdev->req_queue_mutex`, transitions IDLE to VALIDATING, calls `req_validate`, then sets QUEUED before invoking non-failing `req_queue`. Completion happens when bound objects complete/unbind and `num_incomplete_objects` reaches zero, unless manual completion is active. Reinit is allowed only from IDLE or COMPLETE with no active access count, then cleans and returns to IDLE.

State/persistence: requests and objects are in-memory and fd/kref lifetime-managed. State transitions are protected by a spinlock; queue/cancel/update serialization uses `req_queue_mutex`. No durable persistence exists.

Dependencies/integration: depends on media-device request ops, anon inode/file descriptor helpers, spinlocks, waitqueues, krefs, and request-aware users such as V4L2 controls/buffers.

Risks/test signals: object binding assumes request state is UPDATING or QUEUED; invalid state transitions are WARN paths. Completion drops the queue reference via `media_request_put()`, so refcount balance is critical. Tests should cover queue validation failure, queue success with immediate object completion, poll returning `EPOLLPRI`/`EPOLLERR`, reinit busy cases, fd lookup with wrong mdev/fops, object find/get/put lifecycle, manual completion, and cleanup while objects remain bound.
