# File Research: sources/cow-pools/bcachefs/fs/bcachefs/data/extent_update.h

Small public header for atomic extent update trimming.

Key contents:
- Declares `bch2_extent_trim_atomic()`.

Dependencies and interactions:
- Included by extent update/write paths that need to bound transaction iterator pressure before inserting extents.
