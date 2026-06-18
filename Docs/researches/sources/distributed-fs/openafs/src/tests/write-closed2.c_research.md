# sources/distributed-fs/openafs/src/tests/write-closed2.c

Purpose: exercises AFS cache-manager writeback behavior when a file is mmaped, its containing directory ACL is changed to remove access, the descriptor is closed, and the mapped page is modified before `munmap`. It is a regression-style client test for permissions, mmap dirtying, and close/write ordering.

Important APIs and functions: `set_acl` builds a `ViceIoctl` payload for `VIOCSETAL` and calls `pioctl` with follow-symlinks disabled. `doit` creates and enters `bad`, opens/truncates a target file, maps one byte with `MAP_SHARED`, drops directory ACLs to `system:anyuser 0`, closes the fd, writes `0x17` through the mapping, then unmaps. `main` only parses an optional filename.

Control flow/state: the persistent state is the newly created directory and file in the current working directory. The key state transition is fd-open to mmap to ACL-restricted directory to fd-close to mmap write. Dependencies are AFS-specific `pioctl`, `afs/venus.h`, and POSIX mmap/open/truncate calls. Risks include destructive relative paths (`bad`), assuming the current directory is an AFS volume where `VIOCSETAL` works, and only checking syscall failures, not post-write file contents. Test signal is process exit: success means all operations including delayed writeback through `munmap` completed without local errors.
