# sources/distributed-fs/ceph-client/include/drm/drm_flip_work.h

Purpose: Declares a thread-safe utility for deferring work until after a page flip or vblank, commonly to release framebuffers or cursor buffer objects after scanout no longer uses them.

Important APIs, types, and functions: Defines callback type `drm_flip_func_t`, `struct drm_flip_work`, and functions `drm_flip_work_queue()`, `drm_flip_work_commit()`, `drm_flip_work_init()`, and `drm_flip_work_cleanup()`. State includes a debug name, callback, work item, queued list, committed list, and spinlock.

Control flow: Producers queue values into `queued`. When the flip/vblank boundary is reached, `drm_flip_work_commit()` moves queued items to committed under the spinlock and schedules worker execution on the supplied workqueue; the worker calls the callback for each committed item in process context. Commit is safe from atomic context.

State and persistence: State is runtime queue contents and pending work. It persists only for the lifetime of the initialized `drm_flip_work` instance and has no disk persistence.

Dependencies and integration points: Depends on workqueues, spinlocks, lists, and driver page-flip/vblank completion paths. It integrates with legacy display drivers that need delayed unref/free operations outside interrupt context.

Risks and test signals: Risks include cleanup while work is pending, queueing values with insufficient lifetime, calling callbacks in unexpected order, committing to a destroyed workqueue, and leaking queued items on error paths. Test queue/commit from interrupt and process context, cleanup after pending work, multiple commits, empty commits, and framebuffer unref after vblank.
