# File Research: sources/cow-pools/bcachefs-tools/include/linux/swap.h

- Provides `mm_account_reclaimed_pages()`.
- Function is a no-op in userspace.
- Compatibility shim for reclaim-accounting call sites.
