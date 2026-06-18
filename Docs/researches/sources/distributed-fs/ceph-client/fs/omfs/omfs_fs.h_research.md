# sources/distributed-fs/ceph-client/fs/omfs/omfs_fs.h

Purpose: defines the OMFS on-disk constants and packed-by-layout structures used to parse superblocks, root blocks, inode headers, directory/file inode records, and file extent tables.

Important APIs and types: constants include `OMFS_MAGIC`, `OMFS_IMAGIC`, inode type tags (`OMFS_DIR`, `OMFS_FILE`, `OMFS_INODE_*`), layout offsets (`OMFS_DIR_START`, `OMFS_EXTENT_START`, `OMFS_EXTENT_CONT`), `OMFS_NAMELEN`, checksum byte count, and max block/cluster limits. Structures are `omfs_super_block`, `omfs_header`, `omfs_root_block`, `omfs_inode`, `omfs_extent_entry`, and `omfs_extent`.

Control flow: no executable control flow. The constants drive offset arithmetic throughout directory initialization, readdir, file extent mapping, mount validation, and checksum generation.

State and persistence behavior: all multi-byte on-disk fields are big-endian and accessed by callers with `beXX_to_cpu`/`cpu_to_beXX`. Directory blocks store bucket arrays after `OMFS_DIR_START`; file inode blocks store extent tables after `OMFS_EXTENT_START`; continuation blocks store extent tables after `OMFS_EXTENT_CONT`. `omfs_header` carries a self block number, body size, CRC, version, type, magic, and XOR check byte.

Dependencies and integration points: included by `omfs.h` and therefore all OMFS implementation files. Its layout must match the proprietary on-disk format used by Rio Karma and ReplayTV devices, and its max constants are enforced during mount.

Risks: the structures are not explicitly marked packed, so correctness relies on field ordering and natural alignment matching the on-disk format on supported ABIs. No compile-time offset assertions are present. `OMFS_NAMELEN` names may not be NUL-terminated on disk, so callers must use bounded string operations consistently. The max block count and block-size constants are part of the mount-time trust boundary for crafted images.

Test signals: build-time offset/size checks if added, mounting known-good images, fuzzing malformed super/root/inode/extent structures, endian correctness on big- and little-endian systems, names at the 256-byte limit, and checksum validation tests if read-side validation is introduced.
