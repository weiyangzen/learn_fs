<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/integrity.h -->
# sources/distributed-fs/ceph-client/include/linux/integrity.h

Purpose: Declares common integrity subsystem interfaces for xattr-based file metadata and inode attribute change detection.

Important APIs/types/functions: Functions include integrity inode get/set xattr helpers, removal hooks, and `integrity_inode_attrs_changed()` for detecting changes in integrity-relevant inode attributes. `struct integrity_inode_attributes` carries tracked inode metadata fields.

Control flow: Integrity and LSM paths call helpers when reading/writing security xattrs or deciding whether cached appraisal data remains valid.

State/persistence: Integrity metadata persists in filesystem xattrs and cached inode security blobs; this header owns no storage.

Dependencies/integration: Integrates VFS inodes, xattrs, IMA/EVM integrity appraisal, and security hooks.

Risks: Attribute-change detection must match appraisal policy or stale measurements may be trusted.

Test signals: Security xattr get/set/remove, chmod/chown metadata changes, IMA/EVM appraisal invalidation, and filesystems without xattr support.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/integrity.h -->
