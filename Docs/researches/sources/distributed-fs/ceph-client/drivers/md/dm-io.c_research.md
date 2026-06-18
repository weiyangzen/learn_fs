# sources/distributed-fs/ceph-client/drivers/md/dm-io.c

### Purpose
`dm-io.c` implements the Device Mapper helper API for issuing synchronous or asynchronous I/O to one or more block regions from different memory sources. It is used by DM targets to read/write metadata, copy buffers, issue flushes, discards, write-zeroes, and collect per-region errors without open-coding bio allocation and completion tracking.

### Important APIs, Types, And Functions
Public APIs are `dm_io_client_create`, `dm_io_client_destroy`, `dm_io`, `dm_io_init`, and `dm_io_exit`. `struct dm_io_client` owns an I/O mempool and bioset. Internal `struct io` holds `error_bits`, an atomic completion count, callback/context, and optional vmalloc invalidation state. `struct dpages` abstracts page iteration for `DM_IO_PAGE_LIST`, `DM_IO_BIO`, `DM_IO_VMA`, and `DM_IO_KMEM`.

Important functions include `store_io_and_region_in_bio`/`retrieve_io_and_region_from_bio`, `complete_io`, `dec_count`, `endio`, the four dpages initializers, `do_region`, `dispatch_io`, `async_io`, `sync_io`, and `dp_init`.

### Control Flow
`dm_io` validates that multi-region operations are writes, initializes a `dpages` iterator from the caller's memory description, and chooses synchronous or asynchronous execution based on `io_req->notify.fn`. Asynchronous execution allocates `struct io` from a mempool, initializes its count to one, and dispatches one region at a time. Synchronous execution wraps asynchronous execution with a completion and `wait_for_completion_io`.

`do_region` splits a region into one or more bios. For discard and write-zeroes it checks device support and emits segment-sized command bios without data vectors. For data I/O it repeatedly asks `dpages` for pages, fills bios with `bio_add_page`, submits each bio, and increments the shared count before submission. `endio` zero-fills failed reads, decodes the packed region number from `bi_private`, drops the bio, and updates error bits. When the count reaches zero, `complete_io` invalidates vmapped read ranges if necessary, frees the `io`, and calls the client callback.

### State And Persistence Behavior
There is no persistent state. Runtime state is held in per-client pools and per-request `struct io`. Error state is returned as a bitset where each bit corresponds to a region. For VMA reads, the helper flushes the kernel vmap range before issuing I/O and invalidates it after completion.

### Dependencies And Integration Points
The file depends on Device Mapper core helpers, block bios, mempools, biosets, completions, `linux/dm-io.h`, and memory abstractions such as page lists, bio bvecs, vmalloc memory, and direct kernel memory. It is a shared service for many DM targets, including `dm-integrity.c` and `dm-kcopyd.c`.

### Risks And Edge Cases
The `struct io` pointer is packed with a region number in low pointer bits, so the alignment guarantee is critical and enforced with `BUG()`. Multi-region non-write I/O is rejected. Unsupported discard/write-zeroes returns `BLK_STS_NOTSUPP` through the normal completion path. Atomic writes warn if they cannot be submitted as a single bio. Failed reads are zero-filled, which is an intentional data safety behavior but can hide stale buffer contents in tests unless error bits are checked.

### Test Signals
Tests should cover synchronous and asynchronous callbacks, all memory types, multi-region writes with per-region error bits, unsupported discard/write-zeroes, flush-only zero-length regions, VMA cache maintenance, failed read zero-fill, bio splitting over multiple pages, and client create/destroy under memory pressure.
