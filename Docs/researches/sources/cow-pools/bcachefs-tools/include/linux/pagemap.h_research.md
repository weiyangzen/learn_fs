# File Research: sources/cow-pools/bcachefs-tools/include/linux/pagemap.h

Purpose: Defines page-cache readahead page count.

Key APIs:
- `VM_READAHEAD_PAGES (SZ_128K / PAGE_SIZE)`.

Integration:
- Depends on prior definitions of `SZ_128K` and `PAGE_SIZE`.

Risks:
- No include guard or includes; must be included in a context that already defines required size/page macros.
