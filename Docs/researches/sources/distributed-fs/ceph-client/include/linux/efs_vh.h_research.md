# sources/distributed-fs/ceph-client/include/linux/efs_vh.h

Purpose: SGI EFS volume-header on-disk structure definitions for partition and boot-file metadata.

Important APIs/types/functions: constants `VHMAGIC`, `NPARTAB`, `NVDIR`, name-size constants, `struct volume_directory`, `struct partition_table`, `struct volume_header`, partition type constants `SGI_SYSV`, `SGI_EFS`, predicate `IS_EFS()`, and `struct pt_types`.

Control flow: EFS probing code reads a 512-byte volume header, verifies `vh_magic`/checksum, scans `vh_pt[]` for `IS_EFS()` partition types, and uses `vh_vd[]` for boot/header-contained file entries.

State/persistence: all meaningful state is big-endian on-disk metadata. The header defines no mutable runtime state and no functions.

Dependencies/integration: consumed by the EFS filesystem and block/partition probing code. Uses Linux endian integer types to prevent accidental host-endian interpretation.

Risks/test signals: risks are endian conversion mistakes, assuming NUL-terminated fixed-size names, trusting partition counts or logical block numbers without bounds, and checksum mismatch handling. Test with SGI EFS images, sysv-typed EFS CD-ROM partitions, bad magic, corrupt checksum, and truncated headers.
