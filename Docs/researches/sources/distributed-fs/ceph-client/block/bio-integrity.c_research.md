# sources/distributed-fs/ceph-client/block/bio-integrity.c

## Purpose

`bio-integrity.c` implements generic bio integrity payload support. It decides what integrity action a bio needs, allocates and frees payloads and buffers, maps user integrity metadata, clones/trims/advances integrity iterators, and initializes the fallback metadata buffer mempool.

## Important APIs, Types, And Functions

`struct bio_integrity_alloc` contains a payload plus flexible bvec storage. The global `integrity_buf_pool` backs fallback metadata buffers.

Important functions include `__bio_integrity_action()`, `bio_integrity_alloc_buf()`, `bio_integrity_free_buf()`, `bio_integrity_setup_default()`, `bio_integrity_free()`, `bio_integrity_init()`, `bio_integrity_alloc()`, `bio_integrity_map_user()`, `bio_integrity_map_iter()`, `bio_integrity_advance()`, `bio_integrity_trim()`, and `bio_integrity_clone()`.

## Control Flow, State, And Persistence

`__bio_integrity_action()` inspects operation type and device integrity flags. Reads usually need buffering and verification unless offload or `NOVERIFY` avoids it. Writes skip zero-sector flush-like writes and otherwise generate/check metadata, sometimes zeroing larger metadata buffers to avoid leaking uninitialized kernel memory.

`bio_integrity_alloc()` attaches a payload and marks `REQ_INTEGRITY`, while `bio_integrity_free()` clears it. `bio_integrity_alloc_buf()` creates one metadata segment from `kmalloc` or a mempool page and records `BIP_MEMPOOL` ownership.

User mapping validates metadata length and flags, pins/extracts pages, coalesces adjacent pages into bvecs, honors queue integrity segment and DMA alignment limits, marks P2PDMA bios no-merge, and either attaches user bvecs directly or bounces through a copy buffer. Read-copy mode stores original bvecs behind the bounce vector so unmap can copy metadata back.

`bio_integrity_advance()`, `bio_integrity_trim()`, and `bio_integrity_clone()` keep integrity iterators aligned with data bio advance, split, trim, and clone operations.

## Dependencies And Integration Points

The file depends on block integrity profiles, T10 PI, bvec and iov_iter helpers, P2PDMA checks, queue segment limits, and bio crypto state. It is used by automatic integrity, filesystem integrity, user metadata paths, and bio split/clone/advance logic.

## Risks And Test Signals

Ownership is subtle: direct user mappings pin pages, copy mode has different read/write unpin timing, mempool buffers must be freed differently from `kmalloc` buffers, and clones borrow source vectors. Crypto contexts are rejected. Test integrity flags, offload/NOVERIFY/NOGENERATE cases, user metadata alignment and vector limits, partial pin failures, P2PDMA, clone/split/trim/advance, and read copy-back with page refcount checking.
