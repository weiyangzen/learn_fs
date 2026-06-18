<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adfs_fs.h -->
# sources/distributed-fs/ceph-client/include/linux/adfs_fs.h

## Purpose
`adfs_fs.h` wraps ADFS UAPI definitions and provides a boot-block checksum helper for Acorn Disc Filing System media.

## Important APIs, types, and functions
The only local helper is `adfs_checkbblk(unsigned char *ptr)`. It computes an 8-bit checksum over the first 511 bytes of a 512-byte boot block and compares it with byte 511. It returns nonzero when the checksum does not match.

## Control flow
The helper walks backward from byte 510 to byte 0, folding carry into the low byte before adding the next byte. The final folded low byte is compared with the stored checksum.

## State and persistence behavior
No state is stored. The helper observes an on-disk 512-byte block; callers must also validate that the disk size is nonzero because all-zero sectors can appear checksum-valid.

## Dependencies and integration points
It depends on `<uapi/linux/adfs_fs.h>` and integrates with ADFS filesystem mount/validation code.

## Risks and test signals
Risks include passing a buffer shorter than 512 bytes, trusting checksum alone, and endian/algorithm regressions. Test signals include known-good and known-bad boot blocks, all-zero-sector handling, and filesystem mount tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/adfs_fs.h -->
