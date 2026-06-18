# sources/distributed-fs/ceph-client/rust/kernel/page.rs

## Purpose
Provides Rust allocation, ownership, borrowing, mapping, and raw byte-access primitives for kernel pages.

## APIs, Types, and Functions
Exports `PAGE_SHIFT`, `PAGE_SIZE`, `PAGE_MASK`, and `page_align`. `Page` owns a `struct page` allocated by `alloc_pages`; `BorrowedPage<'a>` wraps a non-owning page pointer using `ManuallyDrop<Page>`; `AsPageIter` abstracts page iterators from owning containers. `Page` exposes `alloc_page`, `as_ptr`, `nid`, `read_raw`, `write_raw`, `fill_zero_raw`, and `copy_from_user_slice_raw`.

## Control Flow, State, and Persistence
`alloc_page` converts allocation failure into `AllocError` and transfers page ownership into `Page`; `Drop` releases it with `__free_pages`. Access methods funnel through `with_pointer_into_page`, which validates offset/length against `PAGE_SIZE`, maps the page with `kmap_local_page`, invokes a closure, then unmaps with `kunmap_local`. Borrowed pages deliberately avoid drop-time free.

## Dependencies and Integration
Depends on allocation flags, generated page bindings, `UserSliceReader`, `NonNull`, and local mapping APIs. It integrates with vmalloc-backed allocators through `BorrowedPage` and with user access code through raw copy-from-user support.

## Risks and Test Signals
Risks include integer overflow in `off + len` bounds checking, caller-violated race-freedom requirements for raw reads/writes, using mapped pointers outside the closure or on another task, and treating a borrowed page as owned. Test signals include offset/length boundary tests including overflow-sized inputs, allocation/free leak checks, user-copy short-read/error tests, and KASAN/KCSAN stress around concurrent mappings.
