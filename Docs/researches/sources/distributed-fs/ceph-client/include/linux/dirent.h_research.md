<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dirent.h -->
# sources/distributed-fs/ceph-client/include/linux/dirent.h

## Purpose
Defines the kernel-visible layout of `struct linux_dirent64`, the 64-bit directory entry record used by getdents-style interfaces.

## Important APIs, Types, And Functions
The only type is `struct linux_dirent64` with inode number `d_ino`, offset `d_off`, record length `d_reclen`, type `d_type`, and flexible array filename `d_name[]`.

## Control Flow
The header has no executable control flow. VFS directory iteration code fills records into userspace buffers using this layout.

## State And Persistence
The structure describes transient syscall output. Directory persistence is owned by the filesystem, not this header.

## Dependencies And Integration Points
Depends on fixed-width kernel integer types and integrates with Linux directory syscalls, VFS filldir logic, and libc consumers that parse `linux_dirent64`.

## Risks And Edge Cases
Record length must account for variable name length and alignment. Copying more bytes than the user buffer allows or reporting wrong `d_off` can break directory iteration. `d_type` may be unknown depending on filesystem support.

## Test Signals
Directory syscall tests should cover long names, alignment, buffer-boundary truncation, EOF continuation using `d_off`, and filesystems with and without native file-type reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/dirent.h -->
