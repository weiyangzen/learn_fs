# File Research: sources/cow-pools/bcachefs-tools/fs/init/error_types.h

## Purpose
Defines the `struct bch_fs_errors` state embedded in the filesystem object.

## Main Contents
- Includes superblock error counter types.
- `struct bch_fs_errors` fields:
  - `msgs`, a list of tracked fsck error message states.
  - `msgs_lock`, protecting the message list.
  - `msgs_alloc_err`, recording allocation failure while tracking messages.
  - `counts`, CPU-side superblock error counters.
  - `counts_lock`, protecting counter updates.

## Integration Notes
`error.c` initializes, updates, flushes, and frees this state. The message list backs repeated-error memoization and ratelimiting, while `counts` mirrors persistent superblock error counts.

## Risks and Edge Cases
- If message-state allocation fails, fsck error ratelimiting/memoization may degrade but the filesystem continues reporting.
- The list and count locks protect different parts of the error state and should not be conflated.
