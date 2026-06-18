## sources/distributed-fs/ceph-client/tools/lib/bpf/ringbuf.c

Purpose: Implements libbpf ring buffer consumers for `BPF_MAP_TYPE_RINGBUF` and user-space producers for `BPF_MAP_TYPE_USER_RINGBUF`.

Important APIs/functions: `ring_buffer__new()`, `ring_buffer__add()`, `ring_buffer__poll()`, `ring_buffer__consume[_n]()`, `ring_buffer__free()`, `ring__*()` accessors, `user_ring_buffer__new()`, `user_ring_buffer__reserve[_blocking]()`, `user_ring_buffer__submit()`, and `user_ring_buffer__discard()`.

Control flow: Consumer setup validates map type, mmaps the writable consumer page and read-only producer/data pages, and registers map FDs with epoll. Consumption reads producer/consumer positions with acquire/release barriers, walks committed records, skips discarded records, invokes callbacks, and advances consumer position. User ring buffer setup mmaps consumer read-only plus producer/data read-write pages; reserve checks size, available space, writes a busy header, advances producer position, and submit/discard clears busy with optional discard.

State/persistence: State is in mmapped kernel ring pages plus heap arrays of rings/events. No disk persistence. Epoll FDs and map FDs tie lifetime to kernel objects.

Dependencies/integration: Uses BPF map info syscalls, `mmap`, `epoll`, memory barriers, libbpf option validation, and BPF ring buffer header/flag constants.

Risks: Correctness depends on memory ordering and exact kernel ring layout. Large `max_entries` is guarded against `size_t` overflow. In this checkout `ringbuf_process_ring()` calls `sample_cb` twice for each non-discarded sample, which can duplicate side effects and should fail callback-count tests.

Test signals: Tests should cover wrong map types, wraparound records, busy/discarded records, callback errors, epoll wakeups, user reserve ENOSPC/E2BIG paths, blocking timeout behavior, and callback invocation count.
