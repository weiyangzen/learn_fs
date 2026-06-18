# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/early_alloc.h

## Purpose

This header declares the simple early allocator used while initializing nVHE/pKVM page tables and memory before the normal hyp pool is ready.

## Important APIs, Types, And Functions

APIs are `hyp_early_alloc_init()`, `hyp_early_alloc_nr_used_pages()`, `hyp_early_alloc_page()`, `hyp_early_alloc_contig()`, and exported `hyp_early_alloc_mm_ops`.

## Control Flow

Initialization provides a virtual base and size; later page-table code obtains zeroed pages or contiguous page runs through the mm-ops callbacks.

## State And Persistence Behavior

Implementation stores a bump-pointer range (`base`, `cur`, `end`) and mm operation callbacks. There is no free path.

## Dependencies And Integration Points

It integrates with `struct kvm_pgtable_mm_ops` and nVHE setup/mapping code.

## Risks And Test Signals

Risks are exhausting the early range, requesting zero pages, and leaking allocations because the allocator is monotonic. Test signals include pKVM initialization page counts and failure when the supplied pool is too small.
