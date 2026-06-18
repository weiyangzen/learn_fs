# sources/distributed-fs/ceph-client/drivers/android/binder/allocation.rs

## Purpose

This Rust file models a Binder transaction buffer allocation while the kernel owns or inspects it. It provides bounds-checked read/write/copy helpers over the target process page range, carries cleanup metadata for translated Binder objects and file descriptors, performs fd reservation/installation handoff, releases Binder object refs when the allocation is dropped, and parses serialized Binder object unions safely enough for the Rust Binder transaction path.

## Important APIs, types, and functions

Core types are:

- `AllocationInfo`: optional metadata attached to an allocation, including the offsets range, target node, one-way serialization node, clear-on-free flag, and `FileList`.
- `Allocation`: the live allocation handle. It stores offset, size, user pointer, owning `Arc<Process>`, optional info, drop policy, and debug id.
- `NewAllocation`: transparent wrapper for a newly allocated buffer. Its destructor marks failed transactions unless `success()` is called to extract the allocation.
- `AllocationView<'a>`: bounded view over the data area before offsets; reads/writes/copies through it fail if they exceed `limit`.
- `BinderObject`: C-layout union over UAPI Binder object variants, plus `BinderObjectRef` for typed matching.
- `TranslatedFds`, `Reservation`, `FileList`, `FileEntry`, and `FdsCloseOnFree`: fd translation bookkeeping.

Important methods include `Allocation::copy_into()`, `read()`, `write()`, `fill_zero()`, `keep_alive()`, `set_info_*()`, `info_add_fd_reserve()`, `info_add_fd()`, `translate_fds()`, `looper_need_return_on_free()`, `Drop::drop()`, `AllocationView::transfer_binder_object()`, `AllocationView::cleanup_object()`, `BinderObject::read_from()`, `read_from_inner()`, `as_ref()`, `size()`, and `TranslatedFds::commit()`.

## Control flow

Allocation use starts with `Allocation::new()` after the process allocator has reserved a range and marked pages in use. Transaction-building code copies user data into the allocation, records the offsets range and target/oneway node, collects fds needing translation, and may mark the allocation for zeroing on free. `translate_fds()` reserves new target-process fds with `O_CLOEXEC`, writes those fd numbers into the allocation, traces the receive side, and returns `TranslatedFds`. The caller later calls `commit()` to install files into reserved descriptors and obtain the close-on-free list.

`keep_alive()` transfers a successfully delivered allocation back to the owning `Process` as a freeable buffer and disables automatic free on `Drop`. If the allocation drops normally, cleanup runs: one-way node completion is signaled, target node metadata is cleared, each object in the offsets array is cleaned up through `AllocationView::cleanup_object()`, close-on-free fds are scheduled through `DeferredFdCloser` when running in the owning process group leader, sensitive data is zeroed when requested, and `Process::buffer_raw_free()` frees the raw buffer.

`BinderObject::read_from()` reads only the object size implied by the header while avoiding advancing the caller's `UserSliceReader` until the object type is validated. This prevents extra bytes from becoming a time-of-check/time-of-use surface.

## State and persistence behavior

State lives in the allocation object and in the owning `Process` allocator/page range. The `free_on_drop` flag selects RAII cleanup versus handoff to userspace-freeable state. `AllocationInfo` is intentionally optional, allowing buffers without embedded objects or fd work. File descriptor state is split: reservations are kernel-owned until `TranslatedFds::commit()`, and close-on-free descriptors are retained in `FdsCloseOnFree` for later buffer cleanup. No disk persistence exists.

## Dependencies and integration points

The file depends on Rust-for-Linux kernel APIs for `Arc`, `ARef<File>`, fd reservations, `UserSliceReader`, UAPI Binder structs, transmute traits, allocation vectors, and error codes. It integrates with `Process` page copying and buffer lifecycle methods, `Node`/`NodeRef` reference updates, `DeferredFdCloser` for delayed fd close, `defs.rs` constants/wrappers, and `trace::trace_transaction_fd_recv()`.

## Risks

The largest risks are incorrect bounds checks, mismatched object cleanup, and fd lifetime mistakes. `size_check()` must catch integer overflow and out-of-range access before unsafe page operations. `AllocationView` must keep object parsing inside the intended data region, while direct `alloc` access is reserved for intentional full-allocation operations. Drop cleanup must mirror translation: binder objects increment user refs and handles during delivery, so cleanup must decrement the correct node/ref variant. Deferred close is best effort; allocation failure while creating closers can leave later fds to userspace behavior. `NewAllocation::success()` uses `transmute`, so its transparent layout invariant is critical.

## Test signals

Good coverage includes Rust Binder transaction tests with binder/handle translation in same-process-owner and cross-process cases, fd and fd-array transfer tests, failed transaction cleanup, `TF_CLEAR_BUF` zeroing checks, one-way ordering checks through `pending_oneway_finished()`, invalid object type/offset fuzzing, close-on-free behavior when freeing buffers, and KASAN/KCSAN or Rust Miri-style review of unsafe page access assumptions.
