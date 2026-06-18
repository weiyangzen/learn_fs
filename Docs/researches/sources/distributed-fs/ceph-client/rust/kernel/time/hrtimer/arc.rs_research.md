# Research: sources/distributed-fs/ceph-client/rust/kernel/time/hrtimer/arc.rs

## sources/distributed-fs/ceph-client/rust/kernel/time/hrtimer/arc.rs

Purpose: implements hrtimer pointer and callback support for `Arc<T>`. Important APIs are `ArcHrTimerHandle<T>`, its `HrTimerHandle::cancel` and `Drop`, `HrTimerPointer for Arc<T>`, and `RawHrTimerCallback for Arc<T>`.

Control flow: starting consumes an `Arc<T>`, calls `T::start(Arc::as_ptr(&self), expires)`, and stores the Arc in the handle. Dropping or canceling the handle calls `HrTimer::raw_cancel` on the embedded timer. Callback dispatch casts the C timer to `HrTimer<T>`, finds the enclosing `T`, creates an `ArcBorrow` backed by the handle-owned refcount, builds `HrTimerCallbackContext`, and invokes `T::run`. State is the handle-owned Arc reference. Dependencies include `Arc`, `ArcBorrow`, `HasHrTimer`, `HrTimerCallback`, and core hrtimer traits. Integration points are shared timer owners that may also be referenced elsewhere. Risks include relying on the handle to preserve lifetime, leaked handles keeping objects alive and timers potentially active, wrong callback pointer type bounds, and callback code assuming unique access despite shared Arc semantics. Test signals: clone/start behavior, handle drop cancellation, callback refcount liveness, and cancellation during callback.
