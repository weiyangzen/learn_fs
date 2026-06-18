# File Research: sources/cow-pools/openzfs/lib/libzpool/abd_os.c

Userland ABD OS implementation for libzpool. It simulates kernel scatter/gather ABDs using 4 KiB-aligned iovec-backed allocations.

Key behavior:
- Scatter ABDs use `struct iovec` arrays sized by `abd_iovcnt_for_bytes()`.
- `abd_alloc_struct_impl()` appends variable-length iovec storage to `abd_t` for scatter ABDs.
- `abd_alloc_chunks()` allocates each 4 KiB page with `umem_alloc_aligned()`.
- `abd_zero_scatter` is initialized as a max-block-size scatter ABD whose iovecs all point at one shared zero page.
- `abd_get_offset_scatter()` builds borrowed scatter views by copying iovec entries and setting an intra-page offset.
- Iteration maps either linear memory directly or one scatter page segment at a time.
- Borrow/return helpers allocate temporary buffers for scatter ABDs and assert unchanged data unless the copy-return path is used.

The implementation intentionally creates both linear and scatter ABDs in userland to exercise kernel-like code paths in tests.
