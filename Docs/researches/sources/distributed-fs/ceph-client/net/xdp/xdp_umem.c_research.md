# sources/distributed-fs/ceph-client/net/xdp/xdp_umem.c

Purpose: creates, pins, accounts, maps, refcounts, and releases AF_XDP UMEM regions used as packet buffer memory shared with userspace.

Important APIs/functions: `xdp_umem_create()` validates and creates a UMEM; `xdp_get_umem()` and `xdp_put_umem()` manage references. Internal helpers account locked pages, long-term pin user pages, vmap page arrays, unmap/unpin/unaccount, and optionally defer release via workqueue.

Control flow: registration validates chunk size, flags, page alignment, length overflow, page/chunk counts, power-of-two aligned mode, headroom, and TX metadata length. It sets UMEM geometry, initializes DMA map list and refcount, charges `RLIMIT_MEMLOCK` unless privileged, pins user pages with `FOLL_LONGTERM|FOLL_WRITE`, and vmaps them into `umem->addrs`. Creation allocates an IDA id before registration and cleans up on failure.

State and persistence: per-UMEM state includes ID, user page array, vmap address, size/chunks/pages, flags, headroom, chunk size, optional TX metadata length, user locked-vm accounting, DMA map list, zero-copy flag, and refcount.

Dependencies and integration: used by `xsk.c` socket `XDP_UMEM_REG`, shared by buffer pools in `xsk_buff_pool.c`, and integrates MM long-term pinning, UID accounting, vmalloc/vmap, IDA, and workqueues.

Risks and test signals: pin/account unwind paths and integer validation are critical. Tests should cover invalid flags/chunk/headroom/metadata, aligned versus unaligned chunk geometry, memlock exhaustion, partial pin failures, vmap failure, shared UMEM refcounts, deferred cleanup, and dirty unpin on release.
