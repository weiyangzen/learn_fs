<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ino_bitmap.h -->
# sources/distributed-fs/ceph-client/fs/xfs/scrub/ino_bitmap.h

Purpose: Provides a type-specific bitmap wrapper for individual XFS inode numbers.

Important APIs, types, and functions: Defines `struct xino_bitmap` around `struct xbitmap64`, with inline `xino_bitmap_init()`, `xino_bitmap_destroy()`, `xino_bitmap_set()`, and `xino_bitmap_test()`.

Control flow: Callers initialize the bitmap, add single inode numbers as one-length ranges, query membership with `xino_bitmap_test()`, and destroy the backing bitmap. The test helper uses a one-entry length to ask the generic bitmap whether the inode is covered.

State and persistence: Maintains transient in-memory inode membership only. No on-disk metadata is changed.

Dependencies and integration points: Depends on generic `xbitmap64` and XFS inode number types. It is useful to scrub/repair code that tracks visited, affected, or staged inode sets without mixing address spaces.

Risks and test signals: Watch for allocation failures from `xbitmap64_set`, false positives from range merging, and omitted destruction. Test single insert/test, absent inodes, adjacent inode merging, large inode numbers near filesystem limits, and repeated destroy after empty initialization.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/xfs/scrub/ino_bitmap.h -->
