# sources/distributed-fs/ceph-client/arch/arm64/kvm/hyp/include/nvhe/memory.h

## Purpose

This header defines nVHE hyp memory metadata, address conversion helpers, ownership-state encoding, and `struct hyp_page` refcount helpers.

## Important APIs, Types, And Functions

Important pieces include `enum pkvm_page_state`, `struct hyp_page`, `hyp_phys_to_virt()`, `hyp_virt_to_phys()`, PFN/page conversion macros, `get_host_state()`, `set_host_state()`, `get_hyp_state()`, `set_hyp_state()`, `hyp_page_count()`, `hyp_page_ref_inc()`, `hyp_page_ref_dec()`, `hyp_page_ref_dec_and_test()`, and `hyp_set_page_refcounted()`.

## Control Flow

Most functions are direct conversions or metadata accessors. Hyp-state storage is XOR-compressed with `PKVM_PAGE_STATE_VMEMMAP_MASK` so the vmemmap layout can preserve compact ownership bits.

## State And Persistence Behavior

State lives in the global hyp vmemmap (`hyp_vmemmap`), per-page host/hyp ownership fields, pool pointer/order metadata, and 16-bit refcount.

## Dependencies And Integration Points

It is used by the hyp allocator, memory-protection code, early allocator mm ops, and pKVM ownership selftests.

## Risks And Test Signals

Risks include refcount overflow/underflow, bad phys/virt translation offset, corrupted compact ownership state, and misuse without pool locking. Test signals are page ownership transitions, allocator refcount assertions, pKVM vmemmap backing, and address conversion tests across the hyp VA range.
