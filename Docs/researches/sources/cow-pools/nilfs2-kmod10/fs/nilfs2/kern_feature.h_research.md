# File Research: sources/cow-pools/nilfs2-kmod10/fs/nilfs2/kern_feature.h

## Purpose

Central compatibility header for kernel-version-dependent NILFS2 code paths.

## Main Responsibilities

- Detects or overrides features for RHEL 10 kernel variants and upstream kernel versions.
- Defines `HAVE_FOLIO_BASED_WRITE_BEGIN_END` for folio-based write begin/end APIs introduced around Linux 6.12.
- Defines `HAVE_TIMER_CONTAINER_OF` for `timer_container_of()` availability introduced around Linux 6.16.
- Provides compatibility wrappers:
  - `compat___block_write_begin`
  - `compat_block_write_begin`
  - `compat_block_write_end`
- Provides a fallback mapping from `timer_container_of()` to `from_timer()` when needed.

## Dependencies and Interactions

- Included by `inode.c` for write begin/end signature compatibility.
- Included by `recovery.c` for compatibility block write helpers during roll-forward recovery.
- Depends on `<linux/version.h>` and `<linux/fs.h>`.

## Notable Behaviors and Edge Cases

- Allows build-time override by predefining feature macros as `0` or `1`.
- RHEL 10 handling uses `RHEL_RELEASE_N` when present; otherwise it infers from `RHEL_MINOR`.
- Older page-based write APIs are converted to folio pointers by temporary page variables and `page_folio()`.
