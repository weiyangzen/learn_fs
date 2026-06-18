# sources/distributed-fs/ceph-client/fs/aio.c

Purpose: Implements the legacy Linux native asynchronous I/O syscalls, including context allocation, userspace completion rings, request submission/cancellation, poll/fsync support, event retrieval, and compat/time32 variants.

Important APIs and types: `struct kioctx` owns an AIO context, ring mapping, refcounts, active request list, wait queue, completion state, and per-CPU request accounting. `struct aio_kiocb` wraps read/write, fsync, and poll requests. Syscalls implemented include `io_setup`, `io_destroy`, `io_submit`, `io_cancel`, `io_getevents`, `io_pgetevents`, and compat/time32 forms. `kiocb_set_cancel_fn()` is exported for async file operations to register cancellation.

Control flow: Boot setup creates private slab caches and a pseudo filesystem for AIO rings. `io_setup()` allocates a context, builds a pseudo file, allocates ring folios, mmaps the ring into the caller, and installs the context in `mm->ioctx_table` under RCU. `io_submit()` looks up the context, copies each userspace iocb, allocates an `aio_kiocb`, dispatches to read/write/fsync/poll, and completes or leaves async completion armed. `aio_complete()` writes `struct io_event` into the ring, advances tail with barriers, signals eventfd, and wakes waiters. `io_getevents()` drains ring entries and optionally waits with an hrtimer.

State and persistence: AIO state is per-mm and persists until `io_destroy()` or `exit_aio()`. The user-visible ring stores head/tail and events in mapped folios. Global `aio_nr` and `/proc/sys/fs/aio-*` track and limit request reservations. Active requests are cancelable under `ctx_lock`; completion-space accounting is batched per CPU.

Dependencies and integration points: Integrates with VFS `read_iter`/`write_iter`/`fsync`/`poll`, eventfd, block plugging, memory management, page migration, anonymous pseudo files, security/credentials, RCU, and syscall/compat layers.

Risks: Concurrency is subtle: ring migration, completion IRQ context, user-mutated head, poll waitqueue lifetime, cancellation, and context teardown interact. Request-slot accounting must avoid ring overflow and leaks. Poll supports only one waitqueue per request and has POLLFREE-specific lifetime rules.

Test signals: Context limits and sysctls, mmap/mremap of rings, concurrent submit/getevents, eventfd completion, async write cancellation, poll wake/POLLFREE races, io_destroy waiting for in-flight requests, timeouts/signals in pgetevents, compat pointer/time paths, and page migration of ring folios.
