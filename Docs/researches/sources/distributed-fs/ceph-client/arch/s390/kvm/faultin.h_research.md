# sources/distributed-fs/ceph-client/arch/s390/kvm/faultin.h

## Purpose
Declares the s390 KVM fault-in helpers and provides inline utilities for simple GFN faulting, guest-page reads, releasing arrays of pinned guest faults, and checking invalidation retry needs across multiple faulted pages.

## Important APIs, Types, And Functions
Public declarations are `kvm_s390_faultin_gfn` and `kvm_s390_get_guest_page`. Inline helpers include `kvm_s390_faultin_gfn_simple`, `kvm_s390_get_guest_page_and_read_gpa`, `kvm_s390_release_multiple`, `kvm_s390_multiple_faults_need_retry`, `kvm_s390_get_guest_pages`, and array macros `kvm_s390_release_faultin_array`, `kvm_s390_array_needs_retry_unsafe`, and `kvm_s390_array_needs_retry_safe`.

## Control Flow
Simple callers build a `struct guest_fault` with GFN/write intent and delegate to `kvm_s390_faultin_gfn`. Shadow walkers can pin a page and immediately read an unsigned long from the host mapping via `kvm_s390_get_guest_page_and_read_gpa`. Multi-page users populate an array with `kvm_s390_get_guest_pages`, validate it against a saved invalidation sequence with the retry helpers, and release every valid page through `kvm_s390_release_multiple`.

## State And Persistence
The helpers only operate on caller-owned `struct guest_fault` objects. They set or clear `page`, `pfn`, `valid`, `write_attempt`, and related fields through the underlying implementation. No state is persisted beyond pinned page lifetime and any gmap changes performed by `kvm_s390_faultin_gfn`.

## Dependencies And Integration Points
Includes `linux/kvm_host.h` and `dat.h`. It wraps generic KVM page fault-in/release contracts and s390 MMU invalidation helpers. `gaccess.c` and `gmap.c` use the array helpers heavily while protecting vSIE shadow page tables.

## Risks And Edge Cases
The direct read helper dereferences `phys_to_virt(pfn_to_phys(f->pfn) | offset)` and assumes the pinned page remains valid until release. Multi-page retry helpers skip entries not marked valid, so callers must initialize arrays. Release helpers null out `page` but do not reset every other field. The `ignore` argument controls dirty/error accounting through `kvm_release_faultin_page`, so misuse can lose writeback or falsely dirty pages.

## Test Signals
Compile coverage plus nested-vSIE paths are the main signals. Tests should fault arrays of page-table pages, force MMU invalidation retries between pin and use, verify release on success and error paths, and run with debug page refcounting or leak detection.
