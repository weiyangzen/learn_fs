# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/gfp.h

## Purpose

This header declares the nVHE hyp page-pool allocator used after early boot.

## Important APIs, Types, And Functions

`struct hyp_pool` contains a ticket spinlock, buddy free lists, range bounds, and max order. APIs include `hyp_alloc_pages()`, `hyp_split_page()`, `hyp_get_page()`, `hyp_put_page()`, and `hyp_pool_init()`.

## Control Flow

Callers initialize a pool over a PFN range with reserved pages, allocate pages by order, split compound pages, and adjust references. Freed used pages are constrained by allocator semantics and ownership rules.

## State And Persistence Behavior

State lives in the pool lock, free lists, page refcounts, page order metadata, and physical range fields.

## Dependencies And Integration Points

It uses `nvhe/memory.h` for `struct hyp_page` and `nvhe/spinlock.h` for EL2 locking. It backs pKVM VM pools, page tables, and memory-protection operations.

## Risks And Test Signals

Risks are lock misuse, double free/refcount corruption, out-of-range pages, and reserved page handling. Test signals include pKVM page allocation/free stress, lock assertions, and pool initialization with reserved bootstrap pages.
