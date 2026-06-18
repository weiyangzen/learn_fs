# File Research: sources/cow-pools/bcachefs-tools/include/linux/page.h

This header provides page-size constants and virtual-page shims. If not already defined, `PAGE_SIZE` is `4096`, `PAGE_MASK` masks page offsets, and `PAGE_SHIFT` is `12`.

It defines `virt_to_page()`, `offset_in_page()`, `page_address()`, kmap/kunmap no-ops, `PageHighMem()` as false, a static zero page, and `ZERO_PAGE()`. It treats page pointers as address-aligned placeholders rather than real kernel `struct page` objects.
