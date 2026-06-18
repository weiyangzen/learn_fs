<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsverity.h -->
# sources/distributed-fs/ceph-client/include/linux/fsverity.h

Purpose: Declares the interface between filesystems and the fs-verity support layer for read-only file authenticity verification using Merkle trees and file descriptors/descriptors.

Important APIs/types/functions: `FS_VERITY_MAX_DIGEST_SIZE` and `FS_VERITY_MAX_DESCRIPTOR_SIZE` bound digest and descriptor storage. `fsverity_operations` supplies filesystem callbacks: `begin_enable_verity`, `end_enable_verity`, `get_verity_descriptor`, `read_merkle_tree_page`, optional `readahead_merkle_tree`, and `write_merkle_tree_block`. Public helpers include `fsverity_active()`, `fsverity_get_info()`, ioctls for enable/measure/read-metadata, `fsverity_get_digest()`, `fsverity_file_open()`, read verification helpers, and generic Merkle-tree page helpers.

Control flow: Enabling verity begins with filesystem preparation under `i_rwsem`, writes Merkle blocks through the filesystem, and finishes by storing the descriptor and setting `S_VERITY`. Opening a verity inode calls `__fsverity_file_open()` to initialize verification state and reject writes. Reads call block/folio/bio verification helpers and may trigger Merkle readahead.

State and persistence behavior: Persistent state is filesystem-owned descriptor and Merkle tree storage plus an on-disk verity indicator. Runtime state is `fsverity_info`, fetched only after `S_VERITY` is visible; `fsverity_active()` pairs with flag-setting memory barriers.

Dependencies and integration points: Depends on VFS inode/file APIs, folios, bios, crypto hash metadata, UAPI fsverity structs, and SHA-512 sizing. Filesystems integrate by installing `fsverity_operations` and calling open/read verification hooks, after fscrypt open when encryption is combined.

Risks: Filesystem callbacks must handle concurrent descriptor reads and Merkle reads. Missing memory ordering around `S_VERITY` can expose partially initialized state. `!CONFIG_FS_VERITY` stubs return `-EOPNOTSUPP` or warn on impossible verification calls, so callers must respect config and inode flags.

Test signals: Enable/measure/read metadata ioctls on supported filesystems, corrupted data and corrupted Merkle page reads, encrypted verity file opens, descriptor size boundary tests, concurrent reads during initialization, and disabled-config builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/fsverity.h -->
