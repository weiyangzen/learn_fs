## sources/distributed-fs/ceph-client/tools/lib/bpf/zip.c

Purpose: Implements a small read-only ZIP archive reader for locating entries in simple non-ZIP64 archives.

Important APIs/functions: `zip_archive_open()` opens, sizes, mmaps, and parses central-directory metadata. `zip_archive_find_entry()` scans central-directory records for a named file and returns local-file data. `zip_archive_close()` unmaps and frees. Internal helpers validate EOCD, central-directory headers, local-file headers, and bounds via `check_access()`.

Control flow: Open searches backwards from the end for EOCD, validates comment length and central-directory range, rejects multi-disk/ZIP64 markers, then records central-directory offset and record count. Lookup iterates central-directory file headers, filters encrypted/data-descriptor entries, compares exact non-NUL names, and resolves the local header to data pointer/length.

State/persistence: Archive state is a private mmap plus central-directory coordinates. Entry results point into the mmap and are valid until close.

Dependencies/integration: Uses POSIX open/lseek/mmap/munmap and libbpf error-pointer style. `zip.h` exposes the archive and entry types.

Risks: No decompression is performed; callers must inspect `compression`. ZIP64, streaming descriptors, encryption, and multi-part archives are unsupported. All offset arithmetic is guarded, but packed unaligned structs rely on compiler attributes and host endian matching ZIP little-endian assumptions.

Test signals: Test empty/corrupt archives, EOCD comments, unsupported ZIP64/multi-disk/data-descriptor/encrypted entries, duplicate names, compressed vs stored entries, truncated central/local headers, large sizes near `UINT32_MAX`, and result pointer lifetime after close.
