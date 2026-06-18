<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/mmap.c -->
# sources/distributed-fs/ceph-client/fs/ecryptfs/mmap.c

## Purpose
`mmap.c` supplies eCryptfs address-space operations for cached file I/O. It decrypts data read from the lower encrypted file, encrypts dirty upper folios during writeback, maintains eCryptfs metadata file sizes in headers or xattrs, and handles the special "view as encrypted" mode where userspace sees encrypted bytes plus synthetic metadata.

## Important APIs, types, and functions
The exported object is `ecryptfs_aops`. Key helpers include `ecryptfs_writepages`, `ecryptfs_read_folio`, `ecryptfs_write_begin`, `ecryptfs_write_end`, `ecryptfs_copy_up_encrypted_with_header`, `ecryptfs_write_inode_size_to_metadata`, and lower metadata writers for header and xattr storage. It uses `struct ecryptfs_crypt_stat`, `ecryptfs_xattr_cache`, and lower file helpers from `read_write.c`.

## Control flow
Read-folio chooses among direct lower reads for plaintext files, lower encrypted reads for encrypted-view files, xattr-header synthesis for encrypted-view files whose metadata is stored in xattrs, or full page decryption. Write-begin grabs a folio, fills it from lower storage or decrypts it when a partial page write needs existing contents, and extends holes with truncate/zeroing as needed. Write-end writes plaintext lower data for unencrypted files; encrypted files zero the tail beyond EOF, encrypt the folio to lower storage, update upper inode size, and rewrite the size in metadata. Writeback iterates dirty folios and calls `ecryptfs_encrypt_page`.

## State and persistence
Persistent state is the lower file contents plus eCryptfs metadata containing the logical upper size. Depending on `ECRYPTFS_METADATA_IN_XATTR`, the size is stored either in the first eight bytes of the lower file header or inside the lower xattr. Runtime folio state tracks uptodate/error/dirty status and interacts with writeback mapping errors.

## Dependencies and integration points
This file integrates the Linux folio/page-cache write path, xattr APIs, lower VFS reads/writes, eCryptfs crypto routines, and the stacked filesystem inode relationship. It relies on `ecryptfs_encrypt_page`, `ecryptfs_decrypt_page`, metadata packet helpers, and `fsstack_copy_inode_size`.

## Risks and test signals
Risks include stale or corrupt metadata sizes, partial-write data loss when folios are not uptodate, xattr write failures, encrypted-view header synthesis errors, and behavior under blockless builds noted by the `CONFIG_BLOCK` workaround. Test signals include sparse writes, writes crossing EOF, encrypted-view reads with xattr metadata, lower filesystems without xattr support, writeback error propagation, mmap read/write paths, and `bmap` on lower mappings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/fs/ecryptfs/mmap.c -->
