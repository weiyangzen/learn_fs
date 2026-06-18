# sources/distributed-fs/ceph/src/rgw/rgw_lib_frontend.h

Purpose: Declares the librgw process frontend that queues and executes in-process RGW library requests and tracks mounted `RGWLibFS` instances for lifecycle/GC coordination.

Important APIs and types: `RGWLibProcess` derives from `RGWProcess` and stores an access key, mutex/condition variable, generation counter, shutdown flag, and a flat map of mounted filesystems. It exposes `run()`, `checkpoint()`, `stop()`, `register_fs()`, `unregister_fs()`, `enqueue_req()`, regular request handlers, continued request handlers, and `set_access_key()`. `RGWLibFrontend` derives from `RGWProcessFrontend` and wraps process initialization, stop, enqueue, execute, start, and finish APIs.

Control flow: The frontend creates a `RGWLibProcess`. Callers either queue async requests through `enqueue_req()` or execute synchronously through `execute_req()`. Continued requests use `start_req()` and `finish_req()`. `stop()` propagates shutdown to mounted filesystems and wakes the process loop.

State and persistence: Mounted filesystem pointers are registered in a flat map and generation changes invalidate current GC iteration. Request queueing uses inherited `req_throttle` and `req_wq`. This header does not persist data, but process methods execute operations that mutate RGW storage.

Dependencies and integration points: Depends on `rgw_lib.h`, `rgw_file_int.h`, `RGWProcess`, and Boost flat map. It sits between `AppMain` frontend setup and embedded filesystems using librgw.

Risks: Mounted filesystem pointers are raw and rely on external lifetime/reference conventions. `stop()` iterates mounted filesystems without taking the mutex in the inline method, while register/unregister use the mutex; callers need coordinated shutdown. Async `enqueue_req()` transfers ownership to the work queue, so request deletion responsibility is in the handler.

Test signals: Tests should cover register/unregister during process loop, stop wakeups, synchronous versus async request processing, continued request sequencing, throttling behavior, and mounted filesystem shutdown ordering.
