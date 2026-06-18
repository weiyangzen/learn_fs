# sources/distributed-fs/ceph-client/include/linux/earlycpio.h

## Purpose
This header declares a helper for finding files in an early CPIO archive, commonly used during early boot before the full VFS is available.

## Important APIs, types, and functions
`MAX_CPIO_FILE_NAME` is 18. `struct cpio_data` carries a data pointer, size, and fixed-size name. `find_cpio_data(const char *path, void *data, size_t len, long *offset)` searches a CPIO memory range for a named entry and returns its data descriptor.

## Control flow, state, and persistence
No state is stored by the header. The implementation scans an archive buffer and can report the offset of the found entry or scan position.

## Dependencies and integration points
It depends on Linux types and integrates with early initramfs/initrd parsing and boot-time firmware/data loading.

## Risks and test signals
Risks include fixed name buffer truncation, malformed CPIO records, alignment/padding errors, and invalid offset handling. Tests should cover found/missing files, long names, zero-length files, malformed archives, and offset progression.
