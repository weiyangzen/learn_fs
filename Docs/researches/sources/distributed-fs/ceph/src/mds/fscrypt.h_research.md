<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/fscrypt.h -->
## sources/distributed-fs/ceph/src/mds/fscrypt.h

`fscrypt.h` is a small CephFS MDS header defining `ceph_fscrypt_last_block_header`, the metadata prefix used to describe encrypted last-block handling. It carries a format version, compatibility byte, serialized data length, inode `change_attr`, file offset, and encryption block size.

The struct is data-only and has no local encode/decode methods in this file, so any persistence behavior depends on callers treating the layout consistently. `data_len` is documented as the size of `change_attr + file_offset + block_size`, with possible extra block-size data when the final block is in a hole. `file_offset` is zero for a hole or the write offset for the last block. `block_size` is expected to equal the fscrypt block size.

Dependencies are only integer types from the wider Ceph build environment (`__u8`, `uint32_t`, `uint64_t`). Integration is with encrypted file I/O and metadata paths that need to store or interpret the last encrypted block, especially sparse-file hole cases where the data payload may not be a direct file extent.

Risks are mostly ABI/schema risks: no packing directive appears here, so callers must not assume an external wire layout unless an enclosing encoder controls it; version/compat fields need validation by consumers; and inconsistent `data_len` or `block_size` can lead to truncated or over-read encrypted tail data. Test signals are encode/decode or denc tests in consumers, sparse-file encrypted writes, last-block rewrite after inode change-attr changes, and cross-version compatibility cases.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph/src/mds/fscrypt.h -->
