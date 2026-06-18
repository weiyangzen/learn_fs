# File Research: sources/block-storage/parted/libparted/fs/r/fat/traverse.h

Declares FAT directory traversal state and directory-entry helper functions.

Defines:
- `FatTraverseInfo`: filesystem pointer, directory name, legacy-root flag, dirty/eof flags, current buffer, next buffer, and entry buffer.

Exports:
- Traversal begin/complete/child traversal.
- Dirty marking and next-entry iteration.
- Directory-entry first-cluster get/set.
- Length, name, active/file/system/directory/null/first-cluster predicates.

Role:
- Used by cluster counting and resize directory reconstruction.
