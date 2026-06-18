<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass2.c -->
# sources/distributed-fs/openafs/src/vfsck/pass2.c

## Purpose
Implements fsck pass 2: verify the directory tree starting at the root inode, repair root inode problems, validate `.` and `..`, remove invalid directory entries, decrement link counts for reachable entries, and prevent directories from referencing internal AFS Vice inodes.

## Important APIs, Types, And Functions
Main functions are `pass2` and `pass2check`. It uses `descend`, `allocdir`, `freeino`, `ginode`, `inodirty`, `direrror`, `getpathname`, `lncntp`, and `statemap`.

## Control Flow
`pass2` handles root inode state first: allocate it if missing, reallocate if bad/duplicate, convert file root to directory if requested, then call `descend`. `pass2check` is invoked for each directory entry. It verifies or synthesizes `.` and `..`, removes extra dot entries, builds the current pathname, rejects out-of-range or unallocated targets, resolves `DCLEAR`/`FCLEAR`, descends into unvisited directories, identifies hard links to already found directories, and decrements expected link counts for files and directories. If a directory references a `VSTATE` Vice inode, it can clear the Vice magic and convert it to a regular file.

## State And Persistence
Pass 2 mutates directory entries, root inode mode, inode state transitions, pathname globals, link count expectations, and possibly Vice inode magic. Its directory changes are persisted through buffer dirty flags.

## Dependencies And Integration Points
It is the main consumer of `dir.c` traversal callbacks and relies on pass 1 classification. Pass 3 expects directories not reached by pass 2 to remain `DSTATE`, and pass 4 expects `lncntp` to hold remaining unmatched link counts.

## Risks And Test Signals
Risks include pathname buffer overflow exits, incorrect repair of dot entries when record space is tight, conversion of Vice inodes referenced by directories, and hard-link-to-directory handling. Tests should cover bad root inode states, missing `.`/`..`, extra dot entries, out-of-range inode numbers, duplicate/bad referenced inodes, directory loops, Vice inode directory references, and nested path traversal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/vfsck/pass2.c -->
