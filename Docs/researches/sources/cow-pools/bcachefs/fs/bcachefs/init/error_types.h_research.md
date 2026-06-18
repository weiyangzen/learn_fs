# File Research: sources/cow-pools/bcachefs/fs/bcachefs/init/error_types.h

This header defines `struct bch_fs_errors`, the filesystem-wide error tracking container.

Fields:
- `msgs`: list of active fsck error message states.
- `msgs_lock`: protects the message list.
- `msgs_alloc_err`: records allocation failure while tracking fsck messages.
- `counts`: CPU-side superblock error counters.
- `counts_lock`: protects counter state.

Role:
- Embedded in `struct bch_fs` and initialized by `error.c`.
