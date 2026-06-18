# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/nvhe/early_alloc.c

## Purpose

This file implements the nVHE early bump allocator and page-table mm-ops used during hyp initialization.

## Important APIs, Types, And Functions

It defines `hyp_early_alloc_mm_ops`, `hyp_physvirt_offset`, static `base/end/cur`, and implements `hyp_early_alloc_nr_used_pages()`, `hyp_early_alloc_contig()`, `hyp_early_alloc_page()`, and `hyp_early_alloc_init()`.

## Control Flow

Initialization sets the allocation range and installs mm-op callbacks for zero-page allocation and phys/virt translation. Contiguous allocation rejects zero-page requests and insufficient space, returns the current pointer, advances by page count, and zeroes the allocation.

## State And Persistence Behavior

Allocator state is a monotonic range; allocations are never freed. `hyp_early_alloc_mm_ops` persists for page-table construction. `hyp_physvirt_offset` is read-only after init.

## Dependencies And Integration Points

It integrates with nVHE setup and KVM page-table code using `struct kvm_pgtable_mm_ops`.

## Risks And Test Signals

Risks are pool exhaustion, alignment assumptions inherited from callers, zeroing too much or too little, and using early mm-ops after the intended init phase. Test signals include used-page counts, pKVM init with small pools, and page-table mappings backed by early allocations.
