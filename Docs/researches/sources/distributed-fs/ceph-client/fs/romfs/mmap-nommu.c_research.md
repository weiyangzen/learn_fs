# sources/distributed-fs/ceph-client/fs/romfs/mmap-nommu.c

## Purpose
`mmap-nommu.c` provides ROMFS read-only file operations for NOMMU systems backed by directly addressable MTD devices. It allows shared mappings to point through to the underlying MTD storage when the MTD driver supports it.

## Important APIs, Types, And Functions
`romfs_get_unmapped_area()` validates a requested mapping and delegates address selection to `mtd_get_unmapped_area()`. `romfs_mmap_prepare()` allows only NOMMU shared mappings and rejects unsupported private/copy mappings with `-ENOSYS`. `romfs_mmap_capabilities()` returns MTD mapping capabilities or `NOMMU_MAP_COPY` when no MTD exists. `romfs_ro_fops` combines generic read-only read/seek/splice operations with these NOMMU mmap hooks.

## Control Flow
Mapping starts with VFS/NOMMU asking `get_unmapped_area`. The function rejects non-MTD superblocks, mappings beyond inode EOF, nonzero requested addresses, lengths or page offsets beyond the MTD size, and offsets beyond MTD size after adding `ROMFS_I(inode)->i_dataoffset`. It clamps length to the remaining MTD size if needed, delegates to the MTD driver, and maps `-EOPNOTSUPP` to `-ENOSYS`.

`mmap_prepare` is a second gate: only shared NOMMU VMA flags are accepted. Capabilities are reported directly from the MTD device, allowing the NOMMU core to decide whether direct mapping is possible.

## State And Persistence
The file owns no state. It reads inode size, superblock `s_mtd`, MTD size/capabilities, and ROMFS inode data offset. Mappings are runtime VMA state managed by the VM and MTD layers.

## Dependencies And Integration Points
It depends on NOMMU VM APIs, MTD superblock support, `mtd_get_unmapped_area()`, `mtd_mmap_capabilities()`, and ROMFS inode metadata from `internal.h`. It is compiled only for `!MMU && ROMFS_ON_MTD` and supplies the `romfs_ro_fops` declaration used by `super.c` through `internal.h`.

## Risks
Offset arithmetic must prevent mapping beyond EOF, image data, or MTD bounds. Since `offset += i_dataoffset`, malformed inode metadata could otherwise direct mappings outside file data. Rejecting nonzero `addr` is strict but avoids unsupported placement semantics. Returning copy capabilities for non-MTD fallback ensures reads still work, but direct mmap is unavailable.

## Test Signals
Tests should cover shared versus private mappings, mapping exactly at EOF boundaries, pgoff and len overflow-style edge cases, non-MTD fallback, MTD `-EOPNOTSUPP` translation, and correct physical offset including `i_dataoffset`.
