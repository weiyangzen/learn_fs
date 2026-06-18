# File Research: sources/cow-pools/bcachefs-tools/include/linux/closure.h

This header declares the bcache closure framework: a refcounted continuation/wait primitive used to coordinate asynchronous work, synchronous waits, parent-child closure lifetimes, and workqueue continuation dispatch.

Core types are `struct closure_waitlist`, `struct closure`, and `closure_fn`. The closure state is packed into `atomic_t remaining`, with high bits for states such as `CLOSURE_DESTRUCTOR`, `CLOSURE_SLEEPING`, `CLOSURE_WAITING`, and `CLOSURE_RUNNING`, and low bits for the remaining reference count.

Inline helpers cover refcount manipulation (`closure_get()`, `closure_put()`, `closure_get_not_zero()`), synchronous waiting (`closure_sync()`, `closure_sync_timeout()`), initialization (`closure_init()`, stack variants), wakeups, and scheduling through `closure_queue()`. Macros `continue_at()`, `continue_at_nobarrier()`, `closure_return()`, and `closure_return_with_destructor()` encode the continuation model. Wait-event macros build stack closures and loop until a condition or timeout is satisfied.

The file’s comments define an important ownership rule: a running closure owns a refcount and callers are expected to return immediately after `continue_at()`, because the continuation may own or free the surrounding state.
